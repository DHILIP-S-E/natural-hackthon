"""AURA Notification Tasks — Booking reminders, follow-ups, alerts."""
import asyncio
from datetime import datetime, timezone, timedelta
from app.tasks.celery_app import celery_app
from app.database import async_session_factory, generate_uuid


@celery_app.task(name="app.tasks.notification_tasks.send_booking_reminders")
def send_booking_reminders():
    """Send 24h and 2h booking reminders. Runs hourly via Celery Beat."""
    async def _run():
        async with async_session_factory() as db:
            from sqlalchemy import select
            from app.models.booking import Booking, BookingStatus
            from app.models.notification import Notification

            now = datetime.now(timezone.utc)

            # 24h reminders
            window_24h_start = now + timedelta(hours=23)
            window_24h_end = now + timedelta(hours=25)
            result_24 = await db.execute(
                select(Booking).where(
                    Booking.scheduled_at >= window_24h_start,
                    Booking.scheduled_at <= window_24h_end,
                    Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING,
                                         "confirmed", "pending"]),
                    Booking.reminder_sent_24h == False,
                )
            )
            for booking in result_24.scalars().all():
                notif = Notification(
                    id=generate_uuid(),
                    user_id=booking.customer_id,
                    notification_type="booking_reminder",
                    title="Booking Reminder",
                    body=f"Your appointment is tomorrow at {booking.scheduled_at}",
                    channel="email",
                    priority="normal",
                    data={"booking_id": booking.id},
                )
                db.add(notif)
                booking.reminder_sent_24h = True

                # Send email
                from app.models.user import User
                from app.models.service import Service
                user_r = await db.execute(select(User).where(User.id == booking.customer_id))
                cust = user_r.scalar_one_or_none()
                svc_r = await db.execute(select(Service).where(Service.id == booking.service_id)) if booking.service_id else None
                svc = svc_r.scalar_one_or_none() if svc_r else None
                if cust and cust.email:
                    from app.services.email_service import send_booking_reminder
                    await send_booking_reminder(
                        cust.email,
                        f"{cust.first_name} {cust.last_name}",
                        svc.name if svc else "Your appointment",
                        str(booking.scheduled_at),
                    )

            # 2h reminders
            window_2h_start = now + timedelta(hours=1, minutes=30)
            window_2h_end = now + timedelta(hours=2, minutes=30)
            result_2 = await db.execute(
                select(Booking).where(
                    Booking.scheduled_at >= window_2h_start,
                    Booking.scheduled_at <= window_2h_end,
                    Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING,
                                         "confirmed", "pending"]),
                    Booking.reminder_sent_2h == False,
                )
            )
            for booking in result_2.scalars().all():
                notif = Notification(
                    id=generate_uuid(),
                    user_id=booking.customer_id,
                    notification_type="booking_reminder",
                    title="Almost Time!",
                    body=f"Your appointment is in 2 hours",
                    channel="push",
                    priority="high",
                    data={"booking_id": booking.id},
                )
                db.add(notif)
                booking.reminder_sent_2h = True

            await db.commit()

    return asyncio.run(_run())


@celery_app.task(name="app.tasks.notification_tasks.send_quality_alert")
def send_quality_alert(location_id: str, session_id: str, score: float):
    """Send quality alert to manager when session score < 55."""
    async def _run():
        async with async_session_factory() as db:
            from sqlalchemy import select
            from app.models.location import Location
            from app.models.notification import Notification

            location = await db.get(Location, location_id)
            if not location or not location.manager_id:
                return

            notif = Notification(
                id=generate_uuid(),
                user_id=location.manager_id,
                notification_type="quality_flag",
                title="Quality Alert",
                body=f"Service session scored {score:.1f}% — below threshold",
                channel="email",
                priority="urgent",
                data={"session_id": session_id, "score": score},
            )
            db.add(notif)

            # Send email to manager
            from app.models.user import User
            mgr_r = await db.execute(select(User).where(User.id == location.manager_id))
            mgr = mgr_r.scalar_one_or_none()
            if mgr and mgr.email:
                from app.services.email_service import send_quality_alert_email
                await send_quality_alert_email(
                    mgr.email,
                    f"{mgr.first_name} {mgr.last_name}",
                    score,
                )

            await db.commit()

    return asyncio.run(_run())
