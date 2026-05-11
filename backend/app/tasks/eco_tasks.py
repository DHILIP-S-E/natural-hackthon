"""Eco Tasks — Feature 14: Waste anomaly alerts + monthly Green Salon badge."""
import asyncio
from datetime import datetime, timezone, timedelta
from app.tasks.celery_app import celery_app
from app.database import async_session_factory, generate_uuid


ANOMALY_MESSAGE = (
    "⚠️ Waste Alert at {location_name}: Stylist session used {actual:.0f}ml of {product} "
    "vs expected {expected:.0f}ml (2x overuse). Please review and counsel the stylist. "
    "Session ID: {session_id}"
)

GREEN_SALON_MESSAGE = (
    "🌿 Congratulations {location_name}! You are the GREEN SALON OF THE MONTH for {month}! "
    "Your average eco score: {score}/100. Your team's commitment to sustainable beauty is making a difference. "
    "Your Green Salon badge is now active on the AURA platform!"
)


@celery_app.task(name="app.tasks.eco_tasks.send_waste_anomaly_alert")
def send_waste_anomaly_alert(
    location_id: str,
    session_id: str,
    product_name: str,
    expected: float,
    actual: float,
):
    """Alert branch manager when product usage is 2x+ the expected amount."""
    async def _run():
        async with async_session_factory() as db:
            from sqlalchemy import select
            from app.models.location import Location
            from app.models.user import User
            from app.models.notification import Notification
            from app.services.sns_service import send_whatsapp

            location = await db.get(Location, location_id)
            if not location:
                return

            location_name = location.name

            # Notify manager
            if location.manager_id:
                mgr_r = await db.execute(select(User).where(User.id == location.manager_id))
                mgr = mgr_r.scalar_one_or_none()
                if mgr and mgr.phone:
                    msg = ANOMALY_MESSAGE.format(
                        location_name=location_name,
                        actual=actual,
                        product=product_name,
                        expected=expected,
                        session_id=session_id,
                    )
                    await send_whatsapp(mgr.phone, msg)

                    notif = Notification(
                        id=generate_uuid(),
                        user_id=mgr.id,
                        notification_type="eco_waste_anomaly",
                        title="Product Waste Anomaly Detected",
                        body=msg,
                        channel="whatsapp",
                        priority="urgent",
                        data={"session_id": session_id, "product": product_name,
                              "expected": expected, "actual": actual},
                    )
                    db.add(notif)

            await db.commit()

    return asyncio.run(_run())


@celery_app.task(name="app.tasks.eco_tasks.calculate_monthly_green_salon_badge")
def calculate_monthly_green_salon_badge():
    """Run on 1st of each month: find the salon with highest avg eco score last month.
    Sends WhatsApp congratulations to the winner's manager and all regional managers.
    """
    async def _run():
        async with async_session_factory() as db:
            from sqlalchemy import select
            from app.models.location import Location
            from app.models.session import ServiceSession
            from app.models.booking import Booking
            from app.models.user import User, UserRole
            from app.services.sns_service import send_whatsapp

            now = datetime.now(timezone.utc)
            # Last month
            if now.month == 1:
                last_month = 12
                last_year = now.year - 1
            else:
                last_month = now.month - 1
                last_year = now.year

            month_start = datetime(last_year, last_month, 1, tzinfo=timezone.utc)
            if last_month == 12:
                month_end = datetime(last_year + 1, 1, 1, tzinfo=timezone.utc)
            else:
                month_end = datetime(last_year, last_month + 1, 1, tzinfo=timezone.utc)

            MONTH_NAMES = ["", "January", "February", "March", "April", "May", "June",
                           "July", "August", "September", "October", "November", "December"]

            locations_result = await db.execute(
                select(Location).where(Location.is_active == True)
            )
            locations = locations_result.scalars().all()

            best_location = None
            best_score = 0.0

            for loc in locations:
                sessions_result = await db.execute(
                    select(ServiceSession)
                    .join(Booking, ServiceSession.booking_id == Booking.id)
                    .where(
                        Booking.location_id == loc.id,
                        ServiceSession.started_at >= month_start,
                        ServiceSession.started_at < month_end,
                    )
                )
                sessions = sessions_result.scalars().all()

                eco_scores = []
                for s in sessions:
                    for p in (s.products_used or []):
                        if "eco_score" in p:
                            eco_scores.append(p["eco_score"])

                if eco_scores:
                    avg = sum(eco_scores) / len(eco_scores)
                    if avg > best_score:
                        best_score = avg
                        best_location = loc

            if not best_location or best_score < 60:
                return  # No winner if no data or score too low

            # Notify winner's manager
            if best_location.manager_id:
                mgr_r = await db.execute(
                    select(User).where(User.id == best_location.manager_id)
                )
                mgr = mgr_r.scalar_one_or_none()
                if mgr and mgr.phone:
                    msg = GREEN_SALON_MESSAGE.format(
                        location_name=best_location.name,
                        month=MONTH_NAMES[last_month],
                        score=round(best_score, 1),
                    )
                    await send_whatsapp(mgr.phone, msg)

            # Notify all regional managers
            regional_result = await db.execute(
                select(User).where(
                    User.role.in_(["regional_manager", "REGIONAL_MANAGER"]),
                    User.is_active == True,
                )
            )
            for regional_mgr in regional_result.scalars().all():
                if regional_mgr.phone:
                    msg = (
                        f"🌿 Green Salon of the Month — {MONTH_NAMES[last_month]}: "
                        f"{best_location.name} with eco score {round(best_score, 1)}/100. "
                        "Great example for the network!"
                    )
                    await send_whatsapp(regional_mgr.phone, msg)

            await db.commit()

    return asyncio.run(_run())
