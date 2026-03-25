"""Beauty Journey router — AI-generated 3/6 month roadmaps."""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, timezone

from app.database import get_db
from app.dependencies import get_current_user
from app.models import BeautyJourneyPlan
from app.models.customer import CustomerProfile
from app.schemas.common import APIResponse

router = APIRouter(prefix="/journey", tags=["Beauty Journey"])


class JourneyGenerateRequest(BaseModel):
    plan_duration_weeks: int = 12
    primary_goal: str | None = None


async def _resolve_customer_id(customer_id: str, db: AsyncSession, user) -> str | None:
    if customer_id == "me":
        res = await db.execute(select(CustomerProfile).where(CustomerProfile.user_id == str(user.id)))
        customer = res.scalars().first()
        if not customer:
            return None
        return str(customer.id)
    return customer_id


@router.get("/list/{customer_id}", response_model=APIResponse)
async def list_journeys(customer_id: str, limit: int = 20, offset: int = 0,
                        db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    """List beauty journey plans for a customer."""
    target_id = await _resolve_customer_id(customer_id, db, user)
    if not target_id:
        return APIResponse(success=False, message="Customer profile not found")

    stmt = select(BeautyJourneyPlan).where(
        BeautyJourneyPlan.customer_id == target_id
    ).order_by(BeautyJourneyPlan.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
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
    customer_id: str,
    req: JourneyGenerateRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Generate AI-personalized beauty journey plan."""
    from app.services.ai_service import generate_journey_plan

    # Resolve 'me' or find by ID
    target_customer_id = customer_id
    if customer_id == "me":
        res = await db.execute(select(CustomerProfile).where(CustomerProfile.user_id == str(user.id)))
        customer = res.scalars().first()
        if not customer:
            return APIResponse(success=False, message="Customer profile not found for current user")
        target_customer_id = str(customer.id)
    else:
        customer = await db.get(CustomerProfile, customer_id)

    if not customer:
        return APIResponse(success=False, message="Customer profile not found")

    # Fetch customer profile for AI context
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

    goal = req.primary_goal or (customer.primary_goal if customer else None) or "Overall beauty improvement"

    # Generate via AI service (falls back to rule-based)
    ai_result = await generate_journey_plan(
        customer_profile=customer_ctx,
        primary_goal=goal,
        duration_weeks=req.plan_duration_weeks,
    )

    plan = BeautyJourneyPlan(
        customer_id=str(target_customer_id),
        plan_duration_weeks=req.plan_duration_weeks,
        primary_goal=goal,
        milestones=ai_result.get("milestones", []),
        expected_outcomes=ai_result.get("expected_outcomes", {}),
        skin_projection=ai_result.get("skin_projection"),
        recommended_products=ai_result.get("recommended_products", []),
        estimated_total_cost=ai_result.get("estimated_total_cost", 0),
        generated_at=datetime.now(timezone.utc),
        ai_notes=ai_result.get("ai_notes", ""),
    )
    db.add(plan)
    await db.commit()
    return APIResponse(success=True, data={
        "id": str(plan.id), 
        "customer_id": plan.customer_id,
        "plan_duration_weeks": plan.plan_duration_weeks,
        "primary_goal": plan.primary_goal,
        "milestones": plan.milestones,
        "expected_outcomes": plan.expected_outcomes,
        "skin_projection": plan.skin_projection,
        "recommended_products": json.loads(plan.recommended_products) if isinstance(plan.recommended_products, str) else (plan.recommended_products or []),
        "estimated_total_cost": float(plan.estimated_total_cost) if plan.estimated_total_cost else 0,
        "ai_notes": plan.ai_notes,
        "generated_at": str(plan.generated_at) if plan.generated_at else None,
    }, message="Journey plan generated")


@router.get("/{customer_id}", response_model=APIResponse)
async def get_active_journey(customer_id: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    """Get most recent beauty journey for a customer."""
    target_id = await _resolve_customer_id(customer_id, db, user)
    if not target_id:
        return APIResponse(success=False, message="Customer profile not found")

    result = await db.execute(
        select(BeautyJourneyPlan).where(BeautyJourneyPlan.customer_id == target_id)
        .order_by(BeautyJourneyPlan.created_at.desc()).limit(1)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        return APIResponse(success=True, data=None, message="No journey plan found")
    print(f"[DEBUG_JOURNEY] Plan ID {plan.id} has products: {getattr(plan, 'recommended_products', None)}")
    return APIResponse(success=True, data={
        "id": str(plan.id), "customer_id": plan.customer_id,
        "plan_duration_weeks": plan.plan_duration_weeks,
        "primary_goal": plan.primary_goal,
        "milestones": plan.milestones,
        "expected_outcomes": plan.expected_outcomes,
        "skin_projection": plan.skin_projection,
        "recommended_products": json.loads(plan.recommended_products) if isinstance(plan.recommended_products, str) else (plan.recommended_products or []),
        "estimated_total_cost": float(plan.estimated_total_cost) if plan.estimated_total_cost else None,
        "ai_notes": plan.ai_notes,
        "whatsapp_sent": plan.whatsapp_sent,
        "pdf_url": plan.pdf_url,
        "generated_at": str(plan.generated_at) if plan.generated_at else None,
    })


@router.get("/{customer_id}/progress", response_model=APIResponse)
async def journey_progress(customer_id: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    """Get progress against active journey plan milestones."""
    from app.models.booking import Booking, BookingStatus
    from sqlalchemy import func

    target_id = await _resolve_customer_id(customer_id, db, user)
    if not target_id:
        return APIResponse(success=False, message="Customer profile not found")

    # Get active plan
    plan_result = await db.execute(
        select(BeautyJourneyPlan).where(BeautyJourneyPlan.customer_id == target_id)
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
                Booking.customer_id == target_id,
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
async def journey_history(customer_id: str, limit: int = 50, offset: int = 0,
                          db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    target_id = await _resolve_customer_id(customer_id, db, user)
    if not target_id:
        return APIResponse(success=False, message="Customer profile not found")

    result = await db.execute(
        select(BeautyJourneyPlan).where(BeautyJourneyPlan.customer_id == target_id)
        .order_by(BeautyJourneyPlan.created_at.desc())
        .limit(limit).offset(offset)
    )
    plans = result.scalars().all()
    return APIResponse(success=True, data=[{
        "id": str(p.id), "plan_duration_weeks": p.plan_duration_weeks,
        "primary_goal": p.primary_goal,
        "generated_at": str(p.generated_at) if p.generated_at else None,
    } for p in plans])
