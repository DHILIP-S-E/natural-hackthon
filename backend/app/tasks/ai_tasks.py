"""AURA AI Tasks — Background AI generation tasks."""
import asyncio
from app.tasks.celery_app import celery_app
from app.database import async_session_factory


@celery_app.task(name="app.tasks.ai_tasks.generate_soul_reading_async", bind=True, max_retries=2)
def generate_soul_reading_task(self, session_id: str):
    """Generate SOULSKIN soul reading in background."""
    async def _run():
        async with async_session_factory() as db:
            from sqlalchemy import select
            from app.models.soulskin import SoulskinSession
            from app.services.ai_service import generate_soul_reading

            result = await db.execute(select(SoulskinSession).where(SoulskinSession.id == session_id))
            session = result.scalar_one_or_none()
            if not session:
                return {"error": "Session not found"}

            ai_result = await generate_soul_reading(
                song=session.question_1_song or "",
                colour=session.question_2_colour or "",
                word=session.question_3_word or "",
            )

            session.archetype = ai_result.get("archetype", "bloom")
            session.soul_reading = ai_result.get("soul_reading", "")
            session.archetype_reason = ai_result.get("archetype_reason", "")
            session.service_protocol = ai_result.get("service_protocol", {})
            session.colour_direction = ai_result.get("colour_direction", {})
            session.sensory_environment = ai_result.get("sensory_environment", {})
            session.touch_protocol = ai_result.get("touch_protocol", {})
            session.custom_formula = ai_result.get("custom_formula", {})
            session.stylist_script = ai_result.get("stylist_script", {})
            session.mirror_monologue = ai_result.get("mirror_monologue", "")
            session.private_life_note = ai_result.get("private_life_note", "")
            session.look_created = ai_result.get("look_created", "")
            session.session_completed = True
            await db.commit()
            return {"archetype": session.archetype, "ai_generated": ai_result.get("_ai_generated", False)}

    return asyncio.run(_run())


@celery_app.task(name="app.tasks.ai_tasks.generate_homecare_async", bind=True, max_retries=2)
def generate_homecare_task(self, plan_id: str, customer_id: str):
    """Generate homecare plan in background."""
    async def _run():
        async with async_session_factory() as db:
            from sqlalchemy import select
            from app.models.homecare import HomecarePlan
            from app.models.customer import CustomerProfile
            from app.services.ai_service import generate_homecare_plan

            cp = await db.execute(select(CustomerProfile).where(CustomerProfile.id == customer_id))
            customer = cp.scalar_one_or_none()
            customer_ctx = {}
            if customer:
                customer_ctx = {
                    "hair_type": customer.hair_type, "skin_type": customer.skin_type,
                    "hair_damage_level": customer.hair_damage_level,
                }

            ai_result = await generate_homecare_plan(customer_ctx)

            plan = await db.get(HomecarePlan, plan_id)
            if plan:
                plan.hair_routine = ai_result.get("hair_routine", {})
                plan.skin_routine = ai_result.get("skin_routine", {})
                plan.dos = ai_result.get("dos", [])
                plan.donts = ai_result.get("donts", [])
                await db.commit()

    return asyncio.run(_run())


@celery_app.task(name="app.tasks.ai_tasks.generate_journey_async", bind=True, max_retries=2)
def generate_journey_task(self, plan_id: str, customer_id: str, goal: str, weeks: int):
    """Generate beauty journey plan in background."""
    async def _run():
        async with async_session_factory() as db:
            from sqlalchemy import select
            from app.models.journey import BeautyJourneyPlan
            from app.models.customer import CustomerProfile
            from app.services.ai_service import generate_journey_plan

            cp = await db.execute(select(CustomerProfile).where(CustomerProfile.id == customer_id))
            customer = cp.scalar_one_or_none()
            customer_ctx = {}
            if customer:
                customer_ctx = {"hair_damage_level": customer.hair_damage_level, "beauty_score": customer.beauty_score}

            ai_result = await generate_journey_plan(customer_ctx, goal, weeks)

            plan = await db.get(BeautyJourneyPlan, plan_id)
            if plan:
                plan.milestones = ai_result.get("milestones", [])
                plan.expected_outcomes = ai_result.get("expected_outcomes", {})
                plan.ai_notes = ai_result.get("ai_notes", "")
                await db.commit()

    return asyncio.run(_run())
