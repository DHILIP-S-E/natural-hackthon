"""Beauty Journey router — AI-generated 3/6 month roadmaps."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, timezone

from app.database import get_db
from app.dependencies import get_current_user
from app.models import BeautyJourneyPlan
from app.models.customer import CustomerProfile
from app.schemas.common import APIResponse

router = APIRouter(prefix="/journey", tags=["Beauty Journey"])


@router.get("/", response_model=APIResponse)
async def list_journeys(customer_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(
        select(BeautyJourneyPlan).where(BeautyJourneyPlan.customer_id == str(customer_id))
        .order_by(BeautyJourneyPlan.created_at.desc())
    )
    plans = result.scalars().all()
    return APIResponse(success=True, data=[{
        "id": str(p.id), "customer_id": p.customer_id,
        "plan_duration_weeks": p.plan_duration_weeks,
        "primary_goal": p.primary_goal,
        "milestones": p.milestones or [],
        "expected_outcomes": p.expected_outcomes or {},
        "estimated_total_cost": float(p.estimated_total_cost) if p.estimated_total_cost else None,
        "whatsapp_sent": p.whatsapp_sent,
        "generated_at": str(p.generated_at) if p.generated_at else None,
    } for p in plans])


@router.post("/generate/{customer_id}", response_model=APIResponse)
async def generate_journey(
    customer_id: UUID, plan_duration_weeks: int = 12,
    primary_goal: str = None,
    db: AsyncSession = Depends(get_db), user=Depends(get_current_user),
):
    """Generate AI-personalized beauty journey plan."""
    from app.services.ai_service import generate_journey_plan

    # Fetch customer profile for AI context
    customer_ctx = {}
    cp_result = await db.execute(select(CustomerProfile).where(CustomerProfile.id == str(customer_id)))
    customer = cp_result.scalar_one_or_none()
    if customer:
        customer_ctx = {
            "hair_type": customer.hair_type, "hair_texture": customer.hair_texture,
            "hair_damage_level": customer.hair_damage_level,
            "scalp_condition": customer.scalp_condition,
            "skin_type": customer.skin_type, "skin_tone": customer.skin_tone,
            "acne_severity": customer.acne_severity,
            "pigmentation_level": customer.pigmentation_level,
            "dominant_archetype": customer.dominant_archetype,
            "beauty_score": customer.beauty_score,
            "total_visits": customer.total_visits,
        }

    goal = primary_goal or (customer.primary_goal if customer else None) or "Overall beauty improvement"

    # Generate via AI service (falls back to rule-based)
    ai_result = await generate_journey_plan(
        customer_profile=customer_ctx,
        primary_goal=goal,
        duration_weeks=plan_duration_weeks,
    )

    plan = BeautyJourneyPlan(
        customer_id=str(customer_id),
        plan_duration_weeks=plan_duration_weeks,
        primary_goal=goal,
        milestones=ai_result.get("milestones", []),
        expected_outcomes=ai_result.get("expected_outcomes", {}),
        skin_projection=ai_result.get("skin_projection"),
        estimated_total_cost=ai_result.get("estimated_total_cost", 0),
        generated_at=datetime.now(timezone.utc),
        ai_notes=ai_result.get("ai_notes", ""),
    )
    db.add(plan)
    await db.flush()
    return APIResponse(success=True, data={"id": str(plan.id)}, message="Journey plan generated")


@router.get("/{customer_id}", response_model=APIResponse)
async def get_active_journey(customer_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(
        select(BeautyJourneyPlan).where(BeautyJourneyPlan.customer_id == str(customer_id))
        .order_by(BeautyJourneyPlan.created_at.desc()).limit(1)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        return APIResponse(success=True, data=None, message="No journey plan found")
    return APIResponse(success=True, data={
        "id": str(plan.id), "customer_id": plan.customer_id,
        "plan_duration_weeks": plan.plan_duration_weeks,
        "primary_goal": plan.primary_goal,
        "milestones": plan.milestones,
        "expected_outcomes": plan.expected_outcomes,
        "skin_projection": plan.skin_projection,
        "estimated_total_cost": float(plan.estimated_total_cost) if plan.estimated_total_cost else None,
        "ai_notes": plan.ai_notes,
        "whatsapp_sent": plan.whatsapp_sent,
        "pdf_url": plan.pdf_url,
        "generated_at": str(plan.generated_at) if plan.generated_at else None,
    })


@router.get("/{customer_id}/progress", response_model=APIResponse)
async def journey_progress(customer_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    """Get progress against active journey plan milestones."""
    from app.models.booking import Booking, BookingStatus
    from sqlalchemy import func

    # Get active plan
    plan_result = await db.execute(
        select(BeautyJourneyPlan).where(BeautyJourneyPlan.customer_id == str(customer_id))
        .order_by(BeautyJourneyPlan.created_at.desc()).limit(1)
    )
    plan = plan_result.scalar_one_or_none()
    if not plan:
        return APIResponse(success=True, data=None, message="No journey plan found")

    # Count completed bookings since plan creation
    completed_count = 0
    if plan.generated_at:
        count_result = await db.execute(
            select(func.count()).select_from(Booking).where(
                Booking.customer_id == str(customer_id),
                Booking.status == BookingStatus.COMPLETED,
                Booking.created_at >= plan.generated_at,
            )
        )
        completed_count = count_result.scalar() or 0

    milestones = plan.milestones or []
    total_milestones = len(milestones)
    completed_milestones = min(completed_count, total_milestones)
    progress_pct = round(completed_milestones / total_milestones * 100) if total_milestones > 0 else 0

    return APIResponse(success=True, data={
        "plan_id": str(plan.id),
        "primary_goal": plan.primary_goal,
        "total_milestones": total_milestones,
        "completed_milestones": completed_milestones,
        "progress_pct": progress_pct,
        "completed_visits_since_plan": completed_count,
        "milestones": milestones,
    })


@router.get("/{customer_id}/history", response_model=APIResponse)
async def journey_history(customer_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(
        select(BeautyJourneyPlan).where(BeautyJourneyPlan.customer_id == str(customer_id))
        .order_by(BeautyJourneyPlan.created_at.desc())
    )
    plans = result.scalars().all()
    return APIResponse(success=True, data=[{
        "id": str(p.id), "plan_duration_weeks": p.plan_duration_weeks,
        "primary_goal": p.primary_goal,
        "generated_at": str(p.generated_at) if p.generated_at else None,
    } for p in plans])
