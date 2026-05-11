"""Franchise Tasks — Weekly revenue anomaly detection + regional manager digest.

Business rule:
  Every Monday 6:30 AM IST:
    1. Compare each branch's revenue this week vs last week
    2. If drop > 20% → WhatsApp alert to regional manager + corporate
    3. Generate and send weekly network digest to all regional managers
"""
import asyncio
from datetime import datetime, timezone, timedelta
from app.tasks.celery_app import celery_app
from app.database import async_session_factory

REVENUE_DROP_THRESHOLD = 0.20


@celery_app.task(name="app.tasks.franchise_tasks.check_revenue_anomalies")
def check_revenue_anomalies():
    """Runs every Monday 6:30 AM IST. Alerts regional managers of revenue drops."""
    async def _run():
        async with async_session_factory() as db:
            from sqlalchemy import select, func
            from app.models.location import Location
            from app.models.booking import Booking
            from app.models.user import User, UserRole
            from app.services.sns_service import send_whatsapp

            now = datetime.now(timezone.utc)
            this_week = now - timedelta(days=7)
            last_week_start = now - timedelta(days=14)
            last_week_end = this_week

            locations_result = await db.execute(
                select(Location).where(Location.is_active == True)
            )
            locations = locations_result.scalars().all()

            anomalies = []
            for loc in locations:
                lid = str(loc.id)

                tw = await db.execute(
                    select(func.coalesce(func.sum(Booking.total_amount), 0))
                    .where(
                        Booking.location_id == lid,
                        Booking.scheduled_at >= this_week,
                        Booking.status.in_(["completed", "COMPLETED"]),
                    )
                )
                rev_this = float(tw.scalar() or 0)

                lw = await db.execute(
                    select(func.coalesce(func.sum(Booking.total_amount), 0))
                    .where(
                        Booking.location_id == lid,
                        Booking.scheduled_at >= last_week_start,
                        Booking.scheduled_at < last_week_end,
                        Booking.status.in_(["completed", "COMPLETED"]),
                    )
                )
                rev_last = float(lw.scalar() or 0)

                if rev_last == 0:
                    continue

                drop_pct = (rev_last - rev_this) / rev_last
                if drop_pct < REVENUE_DROP_THRESHOLD:
                    continue

                anomalies.append({
                    "name": loc.name,
                    "city": loc.city,
                    "drop_pct": round(drop_pct * 100, 1),
                    "rev_this": rev_this,
                    "rev_last": rev_last,
                    "manager_id": loc.manager_id,
                })

            if not anomalies:
                return

            # Alert regional managers
            regional_result = await db.execute(
                select(User).where(
                    User.role.in_(["regional_manager", "REGIONAL_MANAGER"]),
                    User.is_active == True,
                )
            )
            regional_managers = regional_result.scalars().all()

            summary = "\n".join(
                f"• {a['name']} ({a['city']}): -{a['drop_pct']}% (₹{a['rev_last']:.0f} → ₹{a['rev_this']:.0f})"
                for a in anomalies[:5]
            )
            msg = (
                f"⚠️ AURA Revenue Alert — {len(anomalies)} branch(es) dropped >20% this week:\n\n"
                f"{summary}\n\n"
                f"Open AURA Franchise Dashboard for root cause analysis and recommended actions."
            )

            for rm in regional_managers:
                if rm.phone:
                    await send_whatsapp(rm.phone, msg)

            # Also alert branch managers
            for anomaly in anomalies:
                if anomaly["manager_id"]:
                    mgr = await db.get(User, anomaly["manager_id"])
                    if mgr and mgr.phone:
                        await send_whatsapp(
                            mgr.phone,
                            f"⚠️ Revenue Alert: {anomaly['name']} revenue dropped "
                            f"{anomaly['drop_pct']}% this week vs last week. "
                            f"Please review bookings and check for any operational issues."
                        )

    return asyncio.run(_run())
