"""AuraScore Tasks — Weekly anomaly detection + multi-level alerts.

Business rule:
  If a stylist's avg AuraScore drops ≥ 15 points week-over-week →
  alert the stylist, their branch manager, and the regional manager.
  Alert includes the weakest signal and a coaching hint.
"""
import asyncio
from datetime import datetime, timezone, timedelta
from app.tasks.celery_app import celery_app
from app.database import async_session_factory


SCORE_DROP_THRESHOLD = 15  # points


@celery_app.task(name="app.tasks.aurascore_tasks.weekly_score_anomaly_scan")
def weekly_score_anomaly_scan():
    """Runs every Monday 6 AM IST. Compares last 7 days vs prior 7 days per stylist."""
    async def _run():
        async with async_session_factory() as db:
            from sqlalchemy import select, func
            from app.models.quality import QualityAssessment
            from app.models.staff import StaffProfile
            from app.models.location import Location
            from app.models.user import User, UserRole
            from app.services.sns_service import send_whatsapp, send_push

            now = datetime.now(timezone.utc)
            this_week_start = now - timedelta(days=7)
            last_week_start = now - timedelta(days=14)
            last_week_end = this_week_start

            staff_result = await db.execute(select(StaffProfile))
            all_staff = staff_result.scalars().all()

            for staff in all_staff:
                # This week avg
                tw = await db.execute(
                    select(func.avg(QualityAssessment.overall_score))
                    .where(
                        QualityAssessment.stylist_id == staff.id,
                        QualityAssessment.created_at >= this_week_start,
                        QualityAssessment.overall_score.isnot(None),
                    )
                )
                this_avg = tw.scalar()

                # Last week avg
                lw = await db.execute(
                    select(func.avg(QualityAssessment.overall_score))
                    .where(
                        QualityAssessment.stylist_id == staff.id,
                        QualityAssessment.created_at >= last_week_start,
                        QualityAssessment.created_at < last_week_end,
                        QualityAssessment.overall_score.isnot(None),
                    )
                )
                last_avg = lw.scalar()

                if not this_avg or not last_avg:
                    continue

                drop = float(last_avg) - float(this_avg)
                if drop < SCORE_DROP_THRESHOLD:
                    continue

                # Get weakest signal from most recent flagged assessment
                recent_qa = await db.execute(
                    select(QualityAssessment)
                    .where(
                        QualityAssessment.stylist_id == staff.id,
                        QualityAssessment.created_at >= this_week_start,
                    )
                    .order_by(QualityAssessment.created_at.desc())
                    .limit(1)
                )
                recent = recent_qa.scalar_one_or_none()
                hint = recent.ai_feedback if recent and recent.ai_feedback else "Review recent service performance."

                # Get stylist user
                stylist_user = await db.execute(select(User).where(User.id == staff.user_id))
                stylist = stylist_user.scalar_one_or_none()

                msg_stylist = (
                    f"Hi {stylist.first_name if stylist else 'Stylist'}, your AuraScore dropped "
                    f"{drop:.0f} points this week ({float(last_avg):.0f} → {float(this_avg):.0f}). "
                    f"Focus area: {hint} Your manager has been notified. Let's turn this around!"
                )

                msg_manager = (
                    f"⚠️ AuraScore Alert: {stylist.first_name if stylist else 'A stylist'}'s score "
                    f"dropped {drop:.0f} points this week ({float(last_avg):.0f} → {float(this_avg):.0f}). "
                    f"Coaching needed: {hint}"
                )

                # Alert stylist
                if stylist and stylist.phone:
                    await send_whatsapp(stylist.phone, msg_stylist)
                if stylist and stylist.push_token:
                    await send_push(
                        stylist.push_token,
                        "AuraScore Drop Detected",
                        f"Your score dropped {drop:.0f} pts. Tap to see your dashboard.",
                    )

                # Alert branch manager
                location = await db.get(Location, staff.location_id) if staff.location_id else None
                if location and location.manager_id:
                    mgr = await db.execute(select(User).where(User.id == location.manager_id))
                    manager = mgr.scalar_one_or_none()
                    if manager and manager.phone:
                        await send_whatsapp(manager.phone, msg_manager)

                # Alert regional managers
                regional_result = await db.execute(
                    select(User).where(
                        User.role.in_(["regional_manager", "REGIONAL_MANAGER"]),
                        User.is_active == True,
                    )
                )
                for rm in regional_result.scalars().all():
                    if rm.phone:
                        await send_whatsapp(rm.phone, f"[Regional] {msg_manager}")

    return asyncio.run(_run())


@celery_app.task(name="app.tasks.aurascore_tasks.check_stylist_score_drop")
def check_stylist_score_drop(stylist_id: str):
    """Immediate check after a flagged session. Triggered from aurascore router."""
    async def _run():
        async with async_session_factory() as db:
            from sqlalchemy import select, func
            from app.models.quality import QualityAssessment
            from app.models.staff import StaffProfile
            from app.models.location import Location
            from app.models.user import User
            from app.services.sns_service import send_whatsapp

            now = datetime.now(timezone.utc)
            this_week = now - timedelta(days=7)
            last_week_start = now - timedelta(days=14)

            tw = await db.execute(
                select(func.avg(QualityAssessment.overall_score))
                .where(QualityAssessment.stylist_id == stylist_id,
                       QualityAssessment.created_at >= this_week)
            )
            lw = await db.execute(
                select(func.avg(QualityAssessment.overall_score))
                .where(QualityAssessment.stylist_id == stylist_id,
                       QualityAssessment.created_at >= last_week_start,
                       QualityAssessment.created_at < this_week)
            )
            this_avg = tw.scalar()
            last_avg = lw.scalar()

            if not this_avg or not last_avg:
                return
            drop = float(last_avg) - float(this_avg)
            if drop < SCORE_DROP_THRESHOLD:
                return

            staff = await db.execute(
                select(StaffProfile).where(StaffProfile.id == stylist_id)
            )
            staff_obj = staff.scalar_one_or_none()
            if not staff_obj:
                return

            location = await db.get(Location, staff_obj.location_id) if staff_obj.location_id else None
            if location and location.manager_id:
                mgr_r = await db.execute(select(User).where(User.id == location.manager_id))
                mgr = mgr_r.scalar_one_or_none()
                if mgr and mgr.phone:
                    await send_whatsapp(
                        mgr.phone,
                        f"⚠️ Immediate Quality Flag: A stylist just received a low AuraScore "
                        f"({float(this_avg):.0f}/100). Please review and provide coaching today.",
                    )

    return asyncio.run(_run())
