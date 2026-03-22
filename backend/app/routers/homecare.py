"""Homecare router — AI-personalized home care plan management."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, timezone

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models import HomecarePlan
from app.models.customer import CustomerProfile
from app.schemas.common import APIResponse

router = APIRouter(prefix="/homecare", tags=["Homecare"])


@router.get("/", response_model=APIResponse)
async def list_plans(customer_id: UUID = None, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    q = select(HomecarePlan).order_by(HomecarePlan.created_at.desc())
    if customer_id:
        q = q.where(HomecarePlan.customer_id == str(customer_id))
    result = await db.execute(q.limit(20))
    plans = result.scalars().all()
    return APIResponse(success=True, data=[{
        "id": str(p.id), "customer_id": p.customer_id,
        "soulskin_archetype": p.soulskin_archetype,
        "plan_duration_weeks": p.plan_duration_weeks,
        "hair_routine": p.hair_routine, "skin_routine": p.skin_routine,
        "climate_adjustments": p.climate_adjustments,
        "archetype_rituals": p.archetype_rituals,
        "product_recommendations": p.product_recommendations,
        "dos": p.dos, "donts": p.donts,
        "next_visit_recommendation": p.next_visit_recommendation,
        "whatsapp_sent": p.whatsapp_sent,
        "generated_at": str(p.generated_at) if p.generated_at else None,
    } for p in plans])


@router.post("/generate", response_model=APIResponse)
async def create_plan(
    customer_id: UUID, booking_id: UUID = None,
    soulskin_archetype: str = None, plan_duration_weeks: int = 4,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(["stylist", "salon_manager", "super_admin"])),
):
    """Generate AI-personalized homecare plan based on customer profile + climate."""
    from app.services.ai_service import generate_homecare_plan

    # Fetch customer profile for AI context
    customer_ctx = {}
    cp = await db.execute(select(CustomerProfile).where(CustomerProfile.id == str(customer_id)))
    customer = cp.scalar_one_or_none()
    if customer:
        customer_ctx = {
            "hair_type": customer.hair_type, "hair_texture": customer.hair_texture,
            "hair_porosity": customer.hair_porosity, "scalp_condition": customer.scalp_condition,
            "hair_damage_level": customer.hair_damage_level,
            "skin_type": customer.skin_type, "skin_tone": customer.skin_tone,
            "skin_sensitivity": customer.skin_sensitivity,
            "primary_skin_concerns": customer.primary_skin_concerns,
            "known_allergies": customer.known_allergies,
            "stress_level": customer.stress_level, "diet_type": customer.diet_type,
            "primary_goal": customer.primary_goal,
        }

    # Fetch climate data if customer has a city
    climate_ctx = None
    if customer and customer.city:
        try:
            from app.services.weather_service import get_or_refresh_climate
            climate_rec = await get_or_refresh_climate(customer.city, db)
            if climate_rec:
                climate_ctx = {
                    "temperature": float(climate_rec.temperature_celsius) if climate_rec.temperature_celsius else None,
                    "humidity": float(climate_rec.humidity_pct) if climate_rec.humidity_pct else None,
                    "uv_index": float(climate_rec.uv_index) if climate_rec.uv_index else None,
                    "aqi": float(climate_rec.aqi) if climate_rec.aqi else None,
                }
        except Exception:
            pass

    # Generate via AI service (falls back to rule-based)
    ai_result = await generate_homecare_plan(
        customer_profile=customer_ctx,
        archetype=soulskin_archetype or (customer.dominant_archetype if customer else None),
        climate_data=climate_ctx,
    )

    plan = HomecarePlan(
        customer_id=str(customer_id),
        booking_id=str(booking_id) if booking_id else None,
        soulskin_archetype=soulskin_archetype or (customer.dominant_archetype if customer else None),
        plan_duration_weeks=plan_duration_weeks,
        hair_routine=ai_result.get("hair_routine", {}),
        skin_routine=ai_result.get("skin_routine", {}),
        climate_adjustments=ai_result.get("climate_adjustments"),
        archetype_rituals=ai_result.get("archetype_rituals"),
        product_recommendations=ai_result.get("product_recommendations"),
        dos=ai_result.get("dos", []),
        donts=ai_result.get("donts", []),
        next_visit_recommendation=ai_result.get("next_visit_recommendation"),
        generated_at=datetime.now(timezone.utc),
        ai_notes=f"{'AI-generated' if ai_result.get('_ai_generated') else 'Rule-based'} homecare plan.",
    )
    db.add(plan)
    await db.flush()
    return APIResponse(success=True, data={"id": str(plan.id)}, message="Homecare plan created")


@router.get("/{customer_id}", response_model=APIResponse)
async def get_latest_plan(customer_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(
        select(HomecarePlan).where(HomecarePlan.customer_id == str(customer_id))
        .order_by(HomecarePlan.created_at.desc()).limit(1)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        return APIResponse(success=True, data=None, message="No homecare plan found")
    return APIResponse(success=True, data={
        "id": str(plan.id), "customer_id": plan.customer_id,
        "soulskin_archetype": plan.soulskin_archetype,
        "plan_duration_weeks": plan.plan_duration_weeks,
        "hair_routine": plan.hair_routine, "skin_routine": plan.skin_routine,
        "climate_adjustments": plan.climate_adjustments,
        "archetype_rituals": plan.archetype_rituals,
        "product_recommendations": plan.product_recommendations,
        "dos": plan.dos, "donts": plan.donts,
        "next_visit_recommendation": plan.next_visit_recommendation,
        "ai_notes": plan.ai_notes,
        "whatsapp_sent": plan.whatsapp_sent,
        "pdf_url": plan.pdf_url,
        "generated_at": str(plan.generated_at) if plan.generated_at else None,
    })


@router.get("/{customer_id}/history", response_model=APIResponse)
async def homecare_history(customer_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(
        select(HomecarePlan).where(HomecarePlan.customer_id == str(customer_id))
        .order_by(HomecarePlan.created_at.desc())
    )
    plans = result.scalars().all()
    return APIResponse(success=True, data=[{
        "id": str(plan.id), "soulskin_archetype": plan.soulskin_archetype,
        "plan_duration_weeks": plan.plan_duration_weeks,
        "generated_at": str(plan.generated_at) if plan.generated_at else None,
    } for plan in plans])
