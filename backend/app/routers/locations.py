"""Locations router — CRUD + analytics for salon locations."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db, enum_val
from app.models.user import User, UserRole
from app.models.location import Location
from app.dependencies import get_current_user, require_roles
from app.schemas.common import APIResponse

router = APIRouter(prefix="/locations", tags=["Locations"])


@router.get("", response_model=APIResponse)
async def list_locations(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    city: Optional[str] = None,
    region: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List locations (filtered by role scope)."""
    query = select(Location).where(Location.is_deleted == False)

    # Role-based filtering
    user_role = enum_val(current_user.role)
    if user_role == UserRole.FRANCHISE_OWNER.value:
        query = query.where(Location.franchise_owner_id == current_user.id)
    elif user_role == UserRole.SALON_MANAGER.value:
        query = query.where(Location.manager_id == current_user.id)
    elif user_role == UserRole.REGIONAL_MANAGER.value:
        # Filter by the regions assigned to this regional manager
        # Regional managers see locations in their assigned region(s)
        from app.models.staff import StaffProfile
        staff_result = await db.execute(
            select(StaffProfile).where(StaffProfile.user_id == current_user.id)
        )
        staff = staff_result.scalar_one_or_none()
        if staff and staff.location_id:
            # Get the region of their assigned location
            loc_result = await db.execute(select(Location).where(Location.id == staff.location_id))
            loc = loc_result.scalar_one_or_none()
            if loc and loc.region:
                query = query.where(Location.region == loc.region)

    if city:
        query = query.where(Location.city.ilike(f"%{city}%"))
    if region:
        query = query.where(Location.region.ilike(f"%{region}%"))

    # Count total
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    # Paginate
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    locations = result.scalars().all()

    return APIResponse(
        success=True,
        data={
            "locations": [
                {
                    "id": loc.id,
                    "name": loc.name,
                    "code": loc.code,
                    "city": loc.city,
                    "state": loc.state,
                    "address": loc.address,
                    "phone": loc.phone,
                    "seating_capacity": loc.seating_capacity,
                    "is_active": loc.is_active,
                    "smart_mirror_enabled": loc.smart_mirror_enabled,
                    "soulskin_enabled": loc.soulskin_enabled,
                }
                for loc in locations
            ],
            "total": total,
            "page": page,
            "per_page": per_page,
        },
    )


@router.get("/{location_id}", response_model=APIResponse)
async def get_location(
    location_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get location details."""
    result = await db.execute(
        select(Location).where(Location.id == location_id, Location.is_deleted == False)
    )
    location = result.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    return APIResponse(
        success=True,
        data={
            "id": location.id,
            "name": location.name,
            "code": location.code,
            "address": location.address,
            "city": location.city,
            "state": location.state,
            "pincode": location.pincode,
            "region": location.region,
            "latitude": float(location.latitude) if location.latitude else None,
            "longitude": float(location.longitude) if location.longitude else None,
            "phone": location.phone,
            "email": location.email,
            "seating_capacity": location.seating_capacity,
            "operating_hours": location.operating_hours,
            "smart_mirror_enabled": location.smart_mirror_enabled,
            "soulskin_enabled": location.soulskin_enabled,
            "climate_zone": location.climate_zone,
            "is_active": location.is_active,
            "monthly_revenue_target": float(location.monthly_revenue_target) if location.monthly_revenue_target else None,
        },
    )


@router.post("", response_model=APIResponse)
async def create_location(
    data: dict,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """Create a new location (SUPER_ADMIN only)."""
    location = Location(**data)
    db.add(location)
    await db.flush()
    return APIResponse(success=True, data={"id": location.id}, message="Location created")


@router.patch("/{location_id}", response_model=APIResponse)
async def update_location(
    location_id: str, data: dict,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.SALON_MANAGER])),
    db: AsyncSession = Depends(get_db),
):
    """Update a location."""
    result = await db.execute(select(Location).where(Location.id == location_id))
    location = result.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    allowed = {"name", "address", "phone", "email", "seating_capacity", "operating_hours",
               "smart_mirror_enabled", "soulskin_enabled", "monthly_revenue_target"}
    for k, v in data.items():
        if k in allowed:
            setattr(location, k, v)
    return APIResponse(success=True, message="Location updated")


@router.delete("/{location_id}", response_model=APIResponse)
async def delete_location(
    location_id: str,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete a location (SUPER_ADMIN only)."""
    from datetime import datetime, timezone
    result = await db.execute(select(Location).where(Location.id == location_id))
    location = result.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    location.is_deleted = True
    location.deleted_at = datetime.now(timezone.utc)
    return APIResponse(success=True, message="Location deleted")


@router.get("/{location_id}/staff", response_model=APIResponse)
async def location_staff(
    location_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get staff at a location."""
    from app.models.staff import StaffProfile
    result = await db.execute(
        select(StaffProfile).where(StaffProfile.location_id == location_id)
    )
    staff = result.scalars().all()
    staff_data = []
    for s in staff:
        user_r = await db.execute(select(User).where(User.id == s.user_id))
        u = user_r.scalar_one_or_none()
        staff_data.append({
            "id": s.id, "name": f"{u.first_name} {u.last_name}" if u else "Unknown",
            "skill_level": s.skill_level, "designation": s.designation,
            "is_available": s.is_available, "current_rating": float(s.current_rating or 0),
            "soulskin_certified": s.soulskin_certified,
            "attrition_risk": s.attrition_risk_label,
        })
    return APIResponse(success=True, data=staff_data)


@router.get("/{location_id}/analytics", response_model=APIResponse)
async def location_analytics(
    location_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get analytics for a specific location."""
    from app.models.booking import Booking, BookingStatus
    from app.models.quality import QualityAssessment
    from app.models.soulskin import SoulskinSession

    revenue = (await db.execute(
        select(func.sum(Booking.final_price)).where(
            Booking.location_id == location_id, Booking.status == BookingStatus.COMPLETED
        )
    )).scalar() or 0

    bookings = (await db.execute(
        select(func.count()).select_from(Booking).where(Booking.location_id == location_id)
    )).scalar() or 0

    quality = (await db.execute(
        select(func.avg(QualityAssessment.overall_score)).where(QualityAssessment.location_id == location_id)
    )).scalar() or 0

    soulskin = (await db.execute(
        select(func.count()).select_from(SoulskinSession).where(
            SoulskinSession.location_id == location_id, SoulskinSession.session_completed == True
        )
    )).scalar() or 0

    return APIResponse(success=True, data={
        "revenue": float(revenue), "total_bookings": bookings,
        "avg_quality": round(float(quality), 2), "soulskin_sessions": soulskin,
    })


@router.get("/{location_id}/queue", response_model=APIResponse)
async def location_queue(
    location_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get live queue state for a location."""
    from app.models.queue import SmartQueueEntry, QueueStatus
    result = await db.execute(
        select(SmartQueueEntry).where(
            SmartQueueEntry.location_id == location_id,
            SmartQueueEntry.status.in_([QueueStatus.WAITING, QueueStatus.IN_SERVICE, "waiting", "in_service"]),
        ).order_by(SmartQueueEntry.position_in_queue)
    )
    entries = result.scalars().all()
    return APIResponse(success=True, data=[{
        "id": e.id, "customer_name": e.customer_name,
        "status": str(e.status.value if hasattr(e.status, 'value') else e.status),
        "position": e.position_in_queue, "wait_mins": e.estimated_wait_mins,
    } for e in entries])


@router.get("/{location_id}/climate", response_model=APIResponse)
async def location_climate(
    location_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get today's climate recommendations for a location's city."""
    result = await db.execute(select(Location).where(Location.id == location_id))
    loc = result.scalar_one_or_none()
    if not loc or not loc.city:
        return APIResponse(success=True, data=None, message="Location or city not found")

    from app.services.weather_service import get_or_refresh_climate
    try:
        rec = await get_or_refresh_climate(loc.city, db)
        return APIResponse(success=True, data={
            "city": rec.city, "temperature": float(rec.temperature_celsius) if rec.temperature_celsius else None,
            "humidity": float(rec.humidity_pct) if rec.humidity_pct else None,
            "uv_index": float(rec.uv_index) if rec.uv_index else None,
            "is_alert": rec.is_alert,
            "hair_recommendations": rec.hair_recommendations,
            "skin_recommendations": rec.skin_recommendations,
        })
    except Exception:
        return APIResponse(success=True, data=None, message="Climate data unavailable")
