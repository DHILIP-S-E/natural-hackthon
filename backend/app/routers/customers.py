"""Customers (Beauty Passport) router — CRUD + scan + soul journal + digital twin."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional

from app.database import get_db, enum_val
from app.models.user import User, UserRole
from app.models.customer import CustomerProfile
from app.models.booking import Booking, BookingStatus
from app.dependencies import get_current_user
from app.schemas.common import APIResponse

router = APIRouter(prefix="/customers", tags=["Customers / Beauty Passport"])


@router.get("", response_model=APIResponse)
async def list_customers(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    location_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List customers (Beauty Passports)."""
    query = select(CustomerProfile).options(selectinload(CustomerProfile.user))

    if location_id:
        query = query.where(CustomerProfile.preferred_location_id == location_id)

    # Customer can only see self
    if enum_val(current_user.role) == UserRole.CUSTOMER.value:
        query = query.where(CustomerProfile.user_id == current_user.id)

    total_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(total_q)).scalar() or 0

    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    customers = result.scalars().all()

    return APIResponse(
        success=True,
        data={
            "customers": [
                {
                    "id": c.id,
                    "user_id": c.user_id,
                    "name": f"{c.user.first_name} {c.user.last_name}" if c.user else None,
                    "email": c.user.email if c.user else None,
                    "phone": c.user.phone if c.user else None,
                    "beauty_score": c.beauty_score,
                    "hair_type": c.hair_type,
                    "skin_type": c.skin_type,
                    "dominant_archetype": c.dominant_archetype,
                    "total_visits": c.total_visits,
                    "passport_completeness": c.passport_completeness,
                    "known_allergies": c.known_allergies,
                    "city": c.city,
                }
                for c in customers
            ],
            "total": total,
            "page": page,
            "per_page": per_page,
        },
    )


@router.get("/search", response_model=APIResponse)
async def search_customers(
    q: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Search customers by name, email, or phone."""
    search_term = f"%{q}%"
    result = await db.execute(
        select(CustomerProfile)
        .options(selectinload(CustomerProfile.user))
        .join(User, CustomerProfile.user_id == User.id)
        .where(or_(
            User.first_name.ilike(search_term),
            User.last_name.ilike(search_term),
            User.email.ilike(search_term),
            User.phone.ilike(search_term),
        ))
        .limit(20)
    )
    customers = result.scalars().all()
    return APIResponse(success=True, data=[{
        "id": c.id, "user_id": c.user_id,
        "name": f"{c.user.first_name} {c.user.last_name}" if c.user else None,
        "email": c.user.email if c.user else None,
        "beauty_score": c.beauty_score,
        "dominant_archetype": c.dominant_archetype,
    } for c in customers])


@router.get("/{customer_id}", response_model=APIResponse)
async def get_customer(
    customer_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get full Beauty Passport for a customer."""
    result = await db.execute(
        select(CustomerProfile)
        .options(selectinload(CustomerProfile.user))
        .where(CustomerProfile.id == customer_id)
    )
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Customer can only see self
    if enum_val(current_user.role) == UserRole.CUSTOMER.value and c.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return APIResponse(
        success=True,
        data={
            "id": c.id, "user_id": c.user_id,
            "name": f"{c.user.first_name} {c.user.last_name}" if c.user else None,
            "beauty_score": c.beauty_score, "passport_completeness": c.passport_completeness,
            # Hair
            "hair_type": c.hair_type, "hair_texture": c.hair_texture,
            "hair_porosity": c.hair_porosity, "hair_density": c.hair_density,
            "scalp_condition": c.scalp_condition, "hair_damage_level": c.hair_damage_level,
            "natural_hair_color": c.natural_hair_color, "current_hair_color": c.current_hair_color,
            "chemical_history": c.chemical_history,
            # Skin
            "skin_type": c.skin_type, "skin_tone": c.skin_tone, "undertone": c.undertone,
            "primary_skin_concerns": c.primary_skin_concerns, "skin_sensitivity": c.skin_sensitivity,
            "acne_severity": c.acne_severity, "pigmentation_level": c.pigmentation_level,
            "wrinkle_score": c.wrinkle_score, "hydration_estimate": c.hydration_estimate,
            # Lifestyle
            "city": c.city, "climate_type": c.climate_type,
            "local_uv_index": float(c.local_uv_index) if c.local_uv_index else None,
            "local_humidity": float(c.local_humidity) if c.local_humidity else None,
            "local_aqi": float(c.local_aqi) if c.local_aqi else None,
            "stress_level": c.stress_level, "diet_type": c.diet_type,
            # Safety
            "known_allergies": c.known_allergies, "product_sensitivities": c.product_sensitivities,
            "patch_test_result": c.patch_test_result,
            # Goals
            "primary_goal": c.primary_goal, "goal_progress_pct": c.goal_progress_pct,
            # SOULSKIN
            "dominant_archetype": c.dominant_archetype, "archetype_history": c.archetype_history,
            "emotional_sensitivity": c.emotional_sensitivity,
            # Twin
            "twin_model_url": c.twin_model_url, "simulation_enabled": c.simulation_enabled,
            # Stats
            "total_visits": c.total_visits,
            "lifetime_value": float(c.lifetime_value) if c.lifetime_value else None,
        },
    )


@router.patch("/{customer_id}", response_model=APIResponse)
async def update_customer(
    customer_id: str,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update customer profile (Beauty Passport fields)."""
    result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.id == customer_id)
    )
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Restrict which fields can be updated
    allowed_fields = {
        "hair_type", "hair_texture", "hair_porosity", "hair_density", "scalp_condition",
        "skin_type", "skin_tone", "undertone", "primary_skin_concerns", "skin_sensitivity",
        "city", "sun_exposure", "occupation_type", "water_quality", "sleep_quality",
        "hydration_habit", "stress_level", "diet_type", "upcoming_events",
        "known_allergies", "product_sensitivities", "primary_goal", "goal_timeline_weeks",
        "goal_notes", "preferred_location_id", "preferred_stylist_id",
    }

    for field, value in data.items():
        if field in allowed_fields:
            setattr(customer, field, value)

    return APIResponse(success=True, message="Beauty Passport updated")


@router.get("/{customer_id}/history", response_model=APIResponse)
async def customer_history(
    customer_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get customer's service history timeline."""
    from app.models.service import Service

    # Join Booking with Service to avoid N+1
    result = await db.execute(
        select(Booking, Service.name, Service.category)
        .outerjoin(Service, Booking.service_id == Service.id)
        .where(Booking.customer_id == customer_id, Booking.status == BookingStatus.COMPLETED)
        .order_by(Booking.scheduled_at.desc())
        .limit(50)
    )
    rows = result.all()

    history = []
    for b, svc_name, svc_category in rows:
        history.append({
            "booking_id": b.id, "booking_number": b.booking_number,
            "service_name": svc_name or "Unknown",
            "service_category": svc_category,
            "scheduled_at": str(b.scheduled_at) if b.scheduled_at else None,
            "final_price": float(b.final_price) if b.final_price else None,
            "location_id": b.location_id,
            "soulskin_session_id": b.soulskin_session_id,
        })

    return APIResponse(success=True, data=history)


@router.get("/{customer_id}/recommendations", response_model=APIResponse)
async def customer_recommendations(
    customer_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get AI-generated service recommendations for a customer."""
    result = await db.execute(select(CustomerProfile).where(CustomerProfile.id == customer_id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Use stored recommendations if available, otherwise generate basic ones
    if c.recommended_next_services:
        return APIResponse(success=True, data=c.recommended_next_services)

    # Rule-based fallback recommendations
    recs = []
    if c.hair_damage_level and c.hair_damage_level >= 3:
        recs.append({"service": "Deep Protein Treatment", "reason": "Your hair shows significant damage", "priority": "high"})
    if c.scalp_condition in ["dry", "dandruff"]:
        recs.append({"service": "Scalp Treatment", "reason": f"Address your {c.scalp_condition} scalp condition", "priority": "medium"})
    if c.acne_severity and c.acne_severity >= 3:
        recs.append({"service": "Deep Cleansing Facial", "reason": "Help manage acne and improve skin clarity", "priority": "high"})
    if not recs:
        recs.append({"service": "Hair Spa", "reason": "Maintain your hair health with a relaxing spa treatment", "priority": "low"})

    return APIResponse(success=True, data=recs)


@router.post("/{customer_id}/scan", response_model=APIResponse)
async def scan_customer(
    customer_id: str,
    data: dict = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit image for AI hair/skin analysis and update Beauty Passport."""
    result = await db.execute(select(CustomerProfile).where(CustomerProfile.id == customer_id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")

    # In production: MediaPipe + PyTorch model would analyze the image
    # For now: accept pre-computed analysis data or use rule-based defaults
    scan_data = data or {}

    # Update diagnostic fields from scan
    for field in ["hair_type", "hair_texture", "hair_porosity", "scalp_condition",
                  "hair_damage_level", "skin_type", "skin_tone", "undertone",
                  "acne_severity", "pigmentation_level", "wrinkle_score", "hydration_estimate"]:
        if field in scan_data:
            setattr(c, field, scan_data[field])

    c.last_scan_at = datetime.now(timezone.utc)
    if "scan_image_url" in scan_data:
        c.scan_image_url = scan_data["scan_image_url"]

    # Recalculate beauty score
    scores = []
    if c.hair_damage_level:
        scores.append(max(0, 100 - c.hair_damage_level * 15))
    if c.acne_severity:
        scores.append(max(0, 100 - c.acne_severity * 15))
    if c.pigmentation_level:
        scores.append(max(0, 100 - c.pigmentation_level * 10))
    c.beauty_score = round(sum(scores) / len(scores)) if scores else 50

    # Calculate passport completeness
    filled = sum(1 for f in [c.hair_type, c.skin_type, c.city, c.known_allergies, c.primary_goal] if f)
    c.passport_completeness = min(100, filled * 20)

    return APIResponse(success=True, data={
        "beauty_score": c.beauty_score,
        "passport_completeness": c.passport_completeness,
        "last_scan_at": str(c.last_scan_at),
    }, message="Beauty Passport updated from scan")


@router.post("/{customer_id}/lifestyle", response_model=APIResponse)
async def update_lifestyle(
    customer_id: str,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update lifestyle data for a customer."""
    result = await db.execute(select(CustomerProfile).where(CustomerProfile.id == customer_id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")

    lifestyle_fields = ["city", "sun_exposure", "occupation_type", "water_quality",
                        "sleep_quality", "hydration_habit", "stress_level", "diet_type", "upcoming_events"]
    for field in lifestyle_fields:
        if field in data:
            setattr(c, field, data[field])

    return APIResponse(success=True, message="Lifestyle data updated")


@router.post("/{customer_id}/goal", response_model=APIResponse)
async def set_beauty_goal(
    customer_id: str,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Set or update customer's beauty goal."""
    result = await db.execute(select(CustomerProfile).where(CustomerProfile.id == customer_id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")

    c.primary_goal = data.get("primary_goal", c.primary_goal)
    c.goal_timeline_weeks = data.get("goal_timeline_weeks", c.goal_timeline_weeks)
    c.goal_notes = data.get("goal_notes", c.goal_notes)
    c.goal_progress_pct = data.get("goal_progress_pct", c.goal_progress_pct or 0)

    return APIResponse(success=True, message="Beauty goal updated")


@router.delete("/{customer_id}", response_model=APIResponse)
async def delete_customer(
    customer_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """DPDP Act right to erasure — soft delete customer data."""
    result = await db.execute(select(CustomerProfile).where(CustomerProfile.id == customer_id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Only self or admin can delete
    if enum_val(current_user.role) == UserRole.CUSTOMER.value and c.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only delete your own data")

    # Soft delete user record
    user_result = await db.execute(select(User).where(User.id == c.user_id))
    user = user_result.scalar_one_or_none()
    if user:
        user.is_deleted = True
        user.deleted_at = datetime.now(timezone.utc)
        user.is_active = False

    return APIResponse(success=True, message="Customer data marked for deletion (30-day retention per DPDP Act)")
