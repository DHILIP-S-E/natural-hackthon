"""Staff router — CRUD + performance + skills."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional

from app.database import get_db, enum_val
from app.models.user import User, UserRole
from app.models.staff import StaffProfile
from app.dependencies import get_current_user, require_roles
from app.schemas.common import APIResponse

router = APIRouter(prefix="/staff", tags=["Staff"])


@router.get("", response_model=APIResponse)
async def list_staff(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    location_id: Optional[str] = None,
    skill_level: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List staff profiles."""
    query = select(StaffProfile).options(selectinload(StaffProfile.user))

    if location_id:
        query = query.where(StaffProfile.location_id == location_id)
    if skill_level:
        query = query.where(StaffProfile.skill_level == skill_level)

    total_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(total_q)).scalar() or 0

    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    staff_list = result.scalars().all()

    return APIResponse(
        success=True,
        data={
            "staff": [
                {
                    "id": s.id,
                    "user_id": s.user_id,
                    "employee_id": s.employee_id,
                    "designation": s.designation,
                    "name": f"{s.user.first_name} {s.user.last_name}" if s.user else None,
                    "email": s.user.email if s.user else None,
                    "skill_level": enum_val(s.skill_level) if s.skill_level else None,
                    "specializations": s.specializations,
                    "is_available": s.is_available,
                    "current_rating": float(s.current_rating) if s.current_rating else None,
                    "total_services_done": s.total_services_done,
                    "soulskin_certified": s.soulskin_certified,
                    "attrition_risk_label": enum_val(s.attrition_risk_label) if s.attrition_risk_label else None,
                }
                for s in staff_list
            ],
            "total": total,
            "page": page,
            "per_page": per_page,
        },
    )


@router.get("/{staff_id}", response_model=APIResponse)
async def get_staff(
    staff_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get staff profile details."""
    result = await db.execute(
        select(StaffProfile).options(selectinload(StaffProfile.user)).where(StaffProfile.id == staff_id)
    )
    staff = result.scalar_one_or_none()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    return APIResponse(
        success=True,
        data={
            "id": staff.id,
            "user_id": staff.user_id,
            "employee_id": staff.employee_id,
            "name": f"{staff.user.first_name} {staff.user.last_name}" if staff.user else None,
            "designation": staff.designation,
            "specializations": staff.specializations,
            "skill_level": enum_val(staff.skill_level) if staff.skill_level else None,
            "years_experience": float(staff.years_experience) if staff.years_experience else None,
            "bio": staff.bio,
            "is_available": staff.is_available,
            "current_rating": float(staff.current_rating) if staff.current_rating else None,
            "total_services_done": staff.total_services_done,
            "total_revenue_generated": float(staff.total_revenue_generated) if staff.total_revenue_generated else 0,
            "soulskin_certified": staff.soulskin_certified,
            "attrition_risk_score": float(staff.attrition_risk_score) if staff.attrition_risk_score else None,
            "attrition_risk_label": enum_val(staff.attrition_risk_label) if staff.attrition_risk_label else None,
            "languages_spoken": staff.languages_spoken,
            "portfolio_image_urls": staff.portfolio_image_urls,
            "instagram_handle": staff.instagram_handle,
        },
    )


@router.post("", response_model=APIResponse)
async def create_staff(
    data: dict,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.FRANCHISE_OWNER, UserRole.REGIONAL_MANAGER])),
    db: AsyncSession = Depends(get_db),
):
    """Create a new staff profile."""
    from app.models.staff import SkillLevel
    staff = StaffProfile(
        user_id=data["user_id"],
        location_id=data["location_id"],
        employee_id=data["employee_id"],
        designation=data.get("designation", "Stylist"),
        specializations=data.get("specializations", []),
        skill_level=SkillLevel(data.get("skill_level", "L1")),
        years_experience=data.get("years_experience", 0),
        bio=data.get("bio"),
    )
    db.add(staff)
    await db.commit()
    await db.refresh(staff)
    return APIResponse(success=True, data={"id": staff.id}, message="Staff profile created")


@router.patch("/{staff_id}", response_model=APIResponse)
async def update_staff(
    staff_id: str, data: dict,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.SALON_MANAGER, UserRole.FRANCHISE_OWNER])),
    db: AsyncSession = Depends(get_db),
):
    """Update a staff profile."""
    result = await db.execute(select(StaffProfile).where(StaffProfile.id == staff_id))
    staff = result.scalar_one_or_none()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    for field in ["designation", "specializations", "bio", "is_available", "weekly_off_day",
                  "languages_spoken", "instagram_handle"]:
        if field in data:
            setattr(staff, field, data[field])
    if "skill_level" in data:
        from app.models.staff import SkillLevel
        staff.skill_level = SkillLevel(data["skill_level"])
    await db.commit()
    return APIResponse(success=True, message="Staff profile updated")


@router.delete("/{staff_id}", response_model=APIResponse)
async def delete_staff(
    staff_id: str,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a staff profile."""
    result = await db.execute(select(StaffProfile).where(StaffProfile.id == staff_id))
    staff = result.scalar_one_or_none()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    # Deactivate the user account
    user_result = await db.execute(select(User).where(User.id == staff.user_id))
    user = user_result.scalar_one_or_none()
    if user:
        user.is_deleted = True
    staff.is_available = False
    await db.commit()
    return APIResponse(success=True, message="Staff profile deleted")


@router.get("/{staff_id}/performance", response_model=APIResponse)
async def staff_performance(
    staff_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get staff performance metrics."""
    from app.models.booking import Booking, BookingStatus
    from app.models.quality import QualityAssessment

    result = await db.execute(select(StaffProfile).where(StaffProfile.id == staff_id))
    staff = result.scalar_one_or_none()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    # Count bookings
    booking_count = await db.scalar(
        select(func.count()).where(Booking.stylist_id == staff_id, Booking.status == BookingStatus.COMPLETED)
    )
    # Avg quality
    avg_quality = await db.scalar(
        select(func.avg(QualityAssessment.overall_score)).where(QualityAssessment.stylist_id == staff_id)
    )

    return APIResponse(success=True, data={
        "total_services": staff.total_services_done,
        "completed_bookings": booking_count or 0,
        "avg_quality_score": round(float(avg_quality or 0), 2),
        "current_rating": float(staff.current_rating) if staff.current_rating else 0,
        "total_revenue": float(staff.total_revenue_generated) if staff.total_revenue_generated else 0,
        "skill_level": enum_val(staff.skill_level) if staff.skill_level else None,
        "soulskin_certified": staff.soulskin_certified,
        "attrition_risk_label": enum_val(staff.attrition_risk_label) if staff.attrition_risk_label else None,
    })
