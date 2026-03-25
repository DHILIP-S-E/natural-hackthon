"""Bookings router — CRUD + lifecycle."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db, enum_val
from app.models.user import User, UserRole
from app.models.booking import Booking, BookingStatus
from app.dependencies import get_current_user, require_role, check_booking_ownership
from app.schemas.common import APIResponse
from app.utils.helpers import generate_booking_number

# Track 3 & 5 AI Agent Handlers
from app.agents.track3_personalization import (
    generate_homecare_plan_handler,
    allergy_safety_check_handler,
)
from app.agents.track5_experience import (
    smart_followup_generate_handler,
    SmartFollowupRequest,
)


router = APIRouter(prefix="/bookings", tags=["Bookings"])


# ── Fixed: /today and /slots MUST be before /{booking_id} to avoid route shadowing ──

@router.get("/today", response_model=APIResponse)
async def today_bookings(
    location_id: str = None, stylist_id: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get today's bookings."""
    from datetime import date
    today = date.today()
    from datetime import datetime as dt, time
    day_start = dt.combine(today, time.min)
    day_end = dt.combine(today, time.max)
    q = select(Booking).where(
        Booking.scheduled_at >= day_start,
        Booking.scheduled_at <= day_end,
    ).order_by(Booking.scheduled_at)
    if location_id:
        q = q.where(Booking.location_id == location_id)
    if stylist_id:
        q = q.where(Booking.stylist_id == stylist_id)

    # Customers only see their own bookings
    user_role = enum_val(current_user.role)
    if user_role == UserRole.CUSTOMER.value:
        from app.models.customer import CustomerProfile
        cp_result = await db.execute(
            select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
        )
        cp = cp_result.scalar_one_or_none()
        if cp:
            q = q.where(Booking.customer_id == cp.id)
        else:
            return APIResponse(success=True, data=[])

    result = await db.execute(q)
    bookings = result.scalars().all()
    return APIResponse(success=True, data=[{
        "id": b.id, "booking_number": b.booking_number,
        "customer_id": b.customer_id, "stylist_id": b.stylist_id,
        "service_id": b.service_id, "status": enum_val(b.status),
        "scheduled_at": str(b.scheduled_at) if b.scheduled_at else None,
        "base_price": float(b.base_price) if b.base_price else None,
    } for b in bookings])


@router.get("/slots", response_model=APIResponse)
async def available_slots(
    location_id: str, date_str: str, service_id: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get available booking slots for a date — checks real availability."""
    from datetime import date as date_type
    from app.models.service import Service

    target_date = date_type.fromisoformat(date_str)
    from datetime import datetime as dt, time

    # Get service duration
    slot_duration = 30
    if service_id:
        svc = await db.get(Service, service_id)
        if svc:
            slot_duration = svc.duration_minutes or 30

    # Get all booked slots for this location+date (use range predicate for index)
    day_start = dt.combine(target_date, time.min)
    day_end = dt.combine(target_date, time.max)
    q = select(Booking).where(
        Booking.scheduled_at >= day_start,
        Booking.scheduled_at <= day_end,
        Booking.location_id == location_id,
        Booking.status.notin_([BookingStatus.CANCELLED.value, BookingStatus.NO_SHOW.value,
                                "cancelled", "no_show"]),
    )
    result = await db.execute(q)
    bookings = result.scalars().all()

    # Batch-fetch all service durations to avoid N+1
    service_ids = list({b.service_id for b in bookings if b.service_id})
    service_durations: dict[str, int] = {}
    if service_ids:
        svc_result = await db.execute(
            select(Service.id, Service.duration_minutes).where(Service.id.in_(service_ids))
        )
        service_durations = {row[0]: row[1] or 30 for row in svc_result.all()}

    # Build occupied time ranges (in minutes from midnight)
    occupied = []
    for b in bookings:
        if b.scheduled_at:
            scheduled = b.scheduled_at
            if hasattr(scheduled, 'hour'):
                start_min = scheduled.hour * 60 + scheduled.minute
            else:
                continue
            dur = service_durations.get(b.service_id, 30) if b.service_id else 30
            occupied.append((start_min, start_min + dur))

    # Generate available 30-min slots from 9:00-20:00, excluding occupied
    open_min, close_min = 9 * 60, 20 * 60
    available = []
    t = open_min
    while t + slot_duration <= close_min:
        # Check if this slot overlaps any occupied range
        if not any(occ_start < t + slot_duration and occ_end > t for occ_start, occ_end in occupied):
            h, m = divmod(t, 60)
            available.append(f"{h:02d}:{m:02d}")
        t += 30

    return APIResponse(success=True, data={
        "date": date_str, "slots": available,
        "slot_duration_mins": slot_duration, "total_available": len(available),
    })


# ── List & Create ──

@router.get("", response_model=APIResponse)
async def list_bookings(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    location_id: Optional[str] = None,
    stylist_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List bookings with filters (role-scoped)."""
    query = select(Booking)

    # Role-based filtering: customers only see their own bookings
    user_role = enum_val(current_user.role)
    if user_role == UserRole.CUSTOMER.value:
        from app.models.customer import CustomerProfile
        cp_result = await db.execute(
            select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
        )
        cp = cp_result.scalar_one_or_none()
        if cp:
            query = query.where(Booking.customer_id == cp.id)
        else:
            return APIResponse(success=True, data={"bookings": [], "total": 0, "page": page, "per_page": per_page})
    elif user_role == UserRole.STYLIST.value:
        # Stylists only see bookings assigned to them
        from app.models.staff import StaffProfile
        sp_result = await db.execute(
            select(StaffProfile).where(StaffProfile.user_id == current_user.id)
        )
        sp = sp_result.scalar_one_or_none()
        if sp:
            query = query.where(Booking.stylist_id == sp.id)
        else:
            return APIResponse(success=True, data={"bookings": [], "total": 0, "page": page, "per_page": per_page})
    elif user_role == UserRole.SALON_MANAGER.value:
        # Salon managers see bookings at their locations
        from app.models.location import Location
        loc_result = await db.execute(
            select(Location.id).where(Location.manager_id == current_user.id)
        )
        loc_ids = [row[0] for row in loc_result.all()]
        if loc_ids:
            query = query.where(Booking.location_id.in_(loc_ids))

    if status:
        query = query.where(Booking.status == status)
    if location_id:
        query = query.where(Booking.location_id == location_id)
    if stylist_id:
        query = query.where(Booking.stylist_id == stylist_id)

    total_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(total_q)).scalar() or 0

    query = query.order_by(Booking.scheduled_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    bookings = result.scalars().all()

    return APIResponse(
        success=True,
        data={
            "bookings": [
                {
                    "id": b.id,
                    "booking_number": b.booking_number,
                    "customer_id": b.customer_id,
                    "location_id": b.location_id,
                    "stylist_id": b.stylist_id,
                    "service_id": b.service_id,
                    "status": enum_val(b.status),
                    "scheduled_at": str(b.scheduled_at) if b.scheduled_at else None,
                    "base_price": float(b.base_price) if b.base_price else None,
                    "final_price": float(b.final_price) if b.final_price else None,
                    "payment_status": enum_val(b.payment_status) if b.payment_status else None,
                    "source": enum_val(b.source) if b.source else None,
                }
                for b in bookings
            ],
            "total": total,
            "page": page,
            "per_page": per_page,
        },
    )


@router.post("", response_model=APIResponse)
async def create_booking(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new booking."""
    # Resolve customer_id
    customer_id = data.get("customer_id")
    if not customer_id:
        from app.models.customer import CustomerProfile
        if enum_val(current_user.role) == UserRole.CUSTOMER.value:
            cp_result = await db.execute(
                select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
            )
            cp = cp_result.scalar_one_or_none()
            if cp:
                customer_id = cp.id
            else:
                raise HTTPException(status_code=400, detail="Customer profile not found for user")
        else:
            raise HTTPException(status_code=400, detail="customer_id is required for staff-led bookings")

    # Robust datetime parsing
    scheduled_at = data["scheduled_at"]
    if isinstance(scheduled_at, str):
        try:
            # Handle possible 'T' or space separator
            scheduled_at = datetime.fromisoformat(scheduled_at.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid date format: {scheduled_at}")

    booking = Booking(
        booking_number=generate_booking_number(),
        customer_id=customer_id,
        location_id=data["location_id"],
        service_id=data["service_id"],
        stylist_id=data.get("stylist_id"),
        scheduled_at=scheduled_at,
        base_price=data.get("base_price"),
        final_price=data.get("final_price", data.get("base_price")),
        source=data.get("source", "app"),
        status=BookingStatus.CONFIRMED,
        notes=data.get("notes"),
    )
    db.add(booking)
    await db.commit() # Use commit for persistence
    await db.refresh(booking)
    return APIResponse(
        success=True, 
        data={"id": booking.id, "booking_number": booking.booking_number}, 
        message="Booking created successfully"
    )


# ── Single booking + lifecycle (staff-only for state changes) ──

@router.get("/{booking_id}", response_model=APIResponse)
async def get_booking(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get booking details."""
    await check_booking_ownership(current_user, booking_id, db)
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    return APIResponse(success=True, data={
        "id": booking.id,
        "booking_number": booking.booking_number,
        "customer_id": booking.customer_id,
        "location_id": booking.location_id,
        "stylist_id": booking.stylist_id,
        "service_id": booking.service_id,
        "status": enum_val(booking.status),
        "scheduled_at": str(booking.scheduled_at) if booking.scheduled_at else None,
        "actual_start_at": str(booking.actual_start_at) if booking.actual_start_at else None,
        "actual_end_at": str(booking.actual_end_at) if booking.actual_end_at else None,
        "base_price": float(booking.base_price) if booking.base_price else None,
        "final_price": float(booking.final_price) if booking.final_price else None,
        "payment_status": enum_val(booking.payment_status) if booking.payment_status else None,
        "payment_method": enum_val(booking.payment_method) if booking.payment_method else None,
        "source": enum_val(booking.source) if booking.source else None,
        "notes": booking.notes,
        "soulskin_session_id": booking.soulskin_session_id,
    })


@router.post("/{booking_id}/check-in", response_model=APIResponse)
async def checkin_booking(
    booking_id: str,
    current_user: User = Depends(require_role(["stylist", "salon_manager", "super_admin"])),
    db: AsyncSession = Depends(get_db),
):
    """Check in a customer for their booking (staff only)."""
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = BookingStatus.CHECKED_IN
    return APIResponse(success=True, message="Customer checked in")


@router.post("/{booking_id}/start", response_model=APIResponse)
async def start_booking(
    booking_id: str,
    current_user: User = Depends(require_role(["stylist", "salon_manager", "super_admin"])),
    db: AsyncSession = Depends(get_db),
):
    """Start service for a booking (staff only)."""
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = BookingStatus.IN_PROGRESS
    booking.actual_start_at = datetime.now(timezone.utc)
    return APIResponse(success=True, message="Service started")


@router.post("/{booking_id}/complete", response_model=APIResponse)
async def complete_booking(
    booking_id: str,
    current_user: User = Depends(require_role(["stylist", "salon_manager", "super_admin"])),
    db: AsyncSession = Depends(get_db),
):
    """Complete a booking (staff only)."""
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = BookingStatus.COMPLETED
    booking.actual_end_at = datetime.now(timezone.utc)
    return APIResponse(success=True, message="Booking completed")


@router.post("/{booking_id}/cancel", response_model=APIResponse)
async def cancel_booking(
    booking_id: str,
    cancellation_reason: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a booking (customer can cancel own, staff can cancel any)."""
    await check_booking_ownership(current_user, booking_id, db)
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if enum_val(booking.status) in [BookingStatus.COMPLETED.value, BookingStatus.CANCELLED.value,
                                     "completed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Cannot cancel this booking")
    booking.status = BookingStatus.CANCELLED
    booking.cancellation_reason = cancellation_reason
    booking.cancelled_at = datetime.now(timezone.utc)
    booking.cancelled_by = current_user.id
    return APIResponse(success=True, message="Booking cancelled")


@router.post("/{booking_id}/no-show", response_model=APIResponse)
async def no_show_booking(
    booking_id: str,
    current_user: User = Depends(require_role(["stylist", "salon_manager", "super_admin"])),
    db: AsyncSession = Depends(get_db),
):
    """Mark booking as no-show (staff only)."""
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = BookingStatus.NO_SHOW
    return APIResponse(success=True, message="Marked as no-show")


# ── AI Agent Managed Endpoints (Track 3 & 5) ──

@router.post("/agents/track3/homecare/generate", response_model=APIResponse)
async def generate_homecare_plan_agent(
    customer_id: str = Query(...),
    booking_id: str = Query(...),
    service_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager", "super_admin"])),
):
    """Bridge to generate_homecare_plan_handler."""
    return await generate_homecare_plan_handler(customer_id, booking_id, service_id, db, user)


@router.post("/agents/track3/safety/allergy-check", response_model=APIResponse)
async def allergy_safety_check_agent(
    customer_id: str = Query(...),
    service_id: str = Query(...),
    products: list[str] = Query(default=[], description="List of product names to check"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager", "super_admin"])),
):
    """Bridge to allergy_safety_check_handler."""
    return await allergy_safety_check_handler(customer_id, service_id, products, db, user)


@router.post("/agents/track5/followup/generate", response_model=APIResponse)
async def smart_followup_generate_agent(
    body: SmartFollowupRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager"])),
):
    """Bridge to smart_followup_generate_handler."""
    return await smart_followup_generate_handler(body, db, user)

