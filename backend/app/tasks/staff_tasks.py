"""AURA Staff Tasks — Attrition risk calculation, skill updates."""
import asyncio
from app.tasks.celery_app import celery_app
from app.database import async_session_factory


@celery_app.task(name="app.tasks.staff_tasks.calculate_attrition_risk")
def calculate_attrition_risk():
    """Calculate attrition risk for all staff. Runs weekly via Celery Beat."""
    async def _run():
        async with async_session_factory() as db:
            from sqlalchemy import select, func
            from datetime import datetime, timezone, timedelta
            from app.models.staff import StaffProfile
            from app.models.booking import Booking, BookingStatus
            from app.models.quality import QualityAssessment

            result = await db.execute(select(StaffProfile))
            staff = result.scalars().all()
            now = datetime.now(timezone.utc)
            thirty_days_ago = now - timedelta(days=30)

            for s in staff:
                # Signals: service count trend, quality trend, late arrivals
                recent_services = (await db.execute(
                    select(func.count()).select_from(Booking).where(
                        Booking.stylist_id == s.id,
                        Booking.status == BookingStatus.COMPLETED,
                        Booking.created_at >= thirty_days_ago,
                    )
                )).scalar() or 0

                recent_quality = (await db.execute(
                    select(func.avg(QualityAssessment.overall_score)).where(
                        QualityAssessment.stylist_id == s.id,
                        QualityAssessment.created_at >= thirty_days_ago,
                    )
                )).scalar() or 75

                # Simple attrition risk model
                risk_score = 0.0
                if recent_services < 10:
                    risk_score += 0.3  # Low activity
                if float(recent_quality) < 60:
                    risk_score += 0.3  # Low quality
                if s.years_experience and float(s.years_experience) < 1:
                    risk_score += 0.2  # New hire
                if float(s.current_rating or 0) < 3.5:
                    risk_score += 0.2  # Low rating

                risk_score = min(risk_score, 1.0)
                s.attrition_risk_score = round(risk_score, 2)
                s.attrition_risk_label = (
                    "high" if risk_score >= 0.6 else
                    "medium" if risk_score >= 0.3 else
                    "low"
                )

            await db.commit()
            return {"updated": len(staff)}

    return asyncio.run(_run())
