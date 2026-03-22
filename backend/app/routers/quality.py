"""Quality & Skill Assessment router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, timezone

from app.database import get_db, enum_val
from app.dependencies import get_current_user, require_role
from app.models import QualityAssessment, SkillAssessment
from app.schemas.common import APIResponse

router = APIRouter(prefix="/quality", tags=["Quality"])


# ── Quality Assessments ──

@router.get("/", response_model=APIResponse)
async def list_quality_assessments(
    location_id: UUID = None, stylist_id: UUID = None,
    page: int = 1, per_page: int = 20,
    db: AsyncSession = Depends(get_db), user=Depends(get_current_user),
):
    q = select(QualityAssessment).order_by(QualityAssessment.created_at.desc())
    if location_id:
        q = q.where(QualityAssessment.location_id == str(location_id))
    if stylist_id:
        q = q.where(QualityAssessment.stylist_id == str(stylist_id))
    q = q.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(q)
    assessments = result.scalars().all()
    return APIResponse(success=True, data=[{
        "id": str(a.id), "booking_id": a.booking_id,
        "stylist_id": a.stylist_id, "location_id": a.location_id,
        "service_id": a.service_id,
        "sop_compliance_score": float(a.sop_compliance_score) if a.sop_compliance_score else None,
        "timing_score": float(a.timing_score) if a.timing_score else None,
        "customer_rating": a.customer_rating,
        "manager_rating": a.manager_rating,
        "overall_score": float(a.overall_score) if a.overall_score else None,
        "is_flagged": a.is_flagged,
        "flag_reason": a.flag_reason,
        "soulskin_alignment_score": float(a.soulskin_alignment_score) if a.soulskin_alignment_score else None,
        "ai_feedback": a.ai_feedback,
        "reviewed_by_manager": a.reviewed_by_manager,
        "created_at": str(a.created_at) if a.created_at else None,
    } for a in assessments])


@router.post("/", response_model=APIResponse)
async def create_quality_assessment(
    booking_id: UUID, stylist_id: UUID, location_id: UUID, service_id: UUID,
    session_id: UUID = None,
    sop_compliance_score: float = 0, timing_score: float = 0,
    customer_rating: int = None, manager_rating: int = None,
    soulskin_alignment_score: float = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(["salon_manager", "super_admin"])),
):
    # Calculate overall score
    customer_score = (customer_rating or 3) * 20
    sop_w = sop_compliance_score * 0.25
    timing_w = timing_score * 0.15
    customer_w = customer_score * 0.50
    soulskin_w = (soulskin_alignment_score or 0) * 0.10 if soulskin_alignment_score else 0
    overall = sop_w + timing_w + customer_w + soulskin_w
    if not soulskin_alignment_score:
        overall = sop_compliance_score * 0.30 + timing_score * 0.20 + customer_score * 0.50

    is_flagged = overall < 55

    assessment = QualityAssessment(
        booking_id=str(booking_id), session_id=str(session_id) if session_id else None,
        stylist_id=str(stylist_id), location_id=str(location_id), service_id=str(service_id),
        sop_compliance_score=sop_compliance_score, timing_score=timing_score,
        customer_rating=customer_rating, manager_rating=manager_rating,
        overall_score=round(overall, 2),
        soulskin_alignment_score=soulskin_alignment_score,
        is_flagged=is_flagged,
        flag_reason="Score below threshold" if is_flagged else None,
    )
    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)
    return APIResponse(success=True, data={"id": str(assessment.id), "overall_score": round(overall, 2)},
                       message="Quality assessment created")


@router.get("/{assessment_id}", response_model=APIResponse)
async def get_quality_assessment(assessment_id: UUID, db: AsyncSession = Depends(get_db),
                                 user=Depends(get_current_user)):
    a = await db.get(QualityAssessment, str(assessment_id))
    if not a:
        raise HTTPException(404, "Assessment not found")
    return APIResponse(success=True, data={
        "id": str(a.id), "booking_id": a.booking_id,
        "stylist_id": a.stylist_id, "location_id": a.location_id,
        "service_id": a.service_id,
        "sop_compliance_score": float(a.sop_compliance_score) if a.sop_compliance_score else None,
        "timing_score": float(a.timing_score) if a.timing_score else None,
        "customer_rating": a.customer_rating, "manager_rating": a.manager_rating,
        "overall_score": float(a.overall_score) if a.overall_score else None,
        "before_image_url": a.before_image_url, "after_image_url": a.after_image_url,
        "ai_analysis_result": a.ai_analysis_result,
        "ai_feedback": a.ai_feedback,
        "is_flagged": a.is_flagged, "flag_reason": a.flag_reason,
        "reviewed_by_manager": a.reviewed_by_manager,
        "manager_review_note": a.manager_review_note,
        "soulskin_alignment_score": float(a.soulskin_alignment_score) if a.soulskin_alignment_score else None,
    })


@router.patch("/{assessment_id}/review", response_model=APIResponse)
async def manager_review(assessment_id: UUID, manager_rating: int = None,
                         manager_review_note: str = None,
                         db: AsyncSession = Depends(get_db),
                         user=Depends(require_role(["salon_manager", "super_admin"]))):
    a = await db.get(QualityAssessment, str(assessment_id))
    if not a:
        raise HTTPException(404, "Assessment not found")
    if manager_rating:
        a.manager_rating = manager_rating
    if manager_review_note:
        a.manager_review_note = manager_review_note
    a.reviewed_by_manager = True
    await db.commit()
    return APIResponse(success=True, message="Review submitted")


@router.get("/stats/summary", response_model=APIResponse)
async def quality_stats(location_id: UUID = None, db: AsyncSession = Depends(get_db),
                        user=Depends(get_current_user)):
    q = select(
        func.avg(QualityAssessment.overall_score).label("avg_score"),
        func.avg(QualityAssessment.sop_compliance_score).label("avg_sop"),
        func.avg(QualityAssessment.timing_score).label("avg_timing"),
        func.count(QualityAssessment.id).label("total"),
        func.sum(QualityAssessment.is_flagged.cast(Integer)).label("flagged_count"),
    )
    if location_id:
        q = q.where(QualityAssessment.location_id == str(location_id))
    result = await db.execute(q)
    row = result.one()
    return APIResponse(success=True, data={
        "avg_overall_score": round(float(row.avg_score or 0), 2),
        "avg_sop_compliance": round(float(row.avg_sop or 0), 2),
        "avg_timing_score": round(float(row.avg_timing or 0), 2),
        "total_assessments": row.total,
        "flagged_count": row.flagged_count or 0,
    })


# ── Skill Assessments ──

@router.get("/skills/{staff_id}", response_model=APIResponse)
async def list_skill_assessments(staff_id: UUID, db: AsyncSession = Depends(get_db),
                                 user=Depends(get_current_user)):
    result = await db.execute(
        select(SkillAssessment).where(SkillAssessment.staff_id == str(staff_id))
        .order_by(SkillAssessment.created_at.desc())
    )
    assessments = result.scalars().all()
    return APIResponse(success=True, data=[{
        "id": str(a.id), "staff_id": a.staff_id,
        "assessment_type": enum_val(a.assessment_type) if a.assessment_type else None,
        "service_category": a.service_category,
        "skill_area": a.skill_area,
        "current_level": enum_val(a.current_level) if a.current_level else None,
        "score": float(a.score) if a.score else None,
        "rubric_scores": a.rubric_scores,
        "l2_gap_items": a.l2_gap_items,
        "l3_gap_items": a.l3_gap_items,
        "recommended_training": a.recommended_training,
        "soulskin_certified": a.soulskin_certified,
        "assessment_notes": a.assessment_notes,
        "created_at": str(a.created_at) if a.created_at else None,
    } for a in assessments])


@router.post("/skills", response_model=APIResponse)
async def create_skill_assessment(
    staff_id: UUID, assessment_type: str = "ai",
    service_category: str = None, skill_area: str = None,
    current_level: str = "L1", score: float = 0,
    rubric_scores: dict = None, recommended_training: list = None,
    soulskin_certified: bool = False,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(["salon_manager", "super_admin"])),
):
    from app.models.quality import AssessmentType
    from app.models.staff import SkillLevel

    assessment = SkillAssessment(
        staff_id=str(staff_id),
        assessed_by=user.id,
        assessment_type=AssessmentType(assessment_type),
        service_category=service_category,
        skill_area=skill_area,
        current_level=SkillLevel(current_level),
        score=score,
        rubric_scores=rubric_scores or {},
        recommended_training=recommended_training or [],
        soulskin_certified=soulskin_certified,
    )
    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)
    return APIResponse(success=True, data={"id": str(assessment.id)}, message="Skill assessment created")
