"""Homecare Tasks — Feature 13: Post-Visit AI Home Care Plan.

Beat schedule:
- 30-min post-checkout trigger: Every 15 minutes (checks for recent checkouts)
- Day 7 re-booking nudge: Daily at 11:00 AM IST
"""
import asyncio
from datetime import datetime, timezone, timedelta, date
from app.tasks.celery_app import celery_app
from app.database import async_session_factory, generate_uuid


HOMECARE_MESSAGE = """Hi {name}! 🌿 Here's your personalised home care routine after your {service} today:

{routine}

✨ Your next recommended appointment: {next_appointment}
📅 Book now: https://natural.dhilip.in/app/book

— AURA Beauty Intelligence"""

DAY7_MESSAGE = """Hi {name}! 💆 It's been 7 days since your {service}.

How is your {result_area} holding up? {tip}

Ready for a touch-up? {stylist_name} is available. Book here: https://natural.dhilip.in/app/book"""


@celery_app.task(name="app.tasks.homecare_tasks.send_post_checkout_homecare")
def send_post_checkout_homecare():
    """Find bookings completed in the last 15-45 minutes and send homecare WhatsApp.
    Runs every 15 minutes. The 30-minute window catches most checkouts.
    """
    async def _run():
        async with async_session_factory() as db:
            from sqlalchemy import select
            from app.models.booking import Booking, BookingStatus
            from app.models.customer import CustomerProfile
            from app.models.user import User
            from app.models.service import Service
            from app.models.notification import Notification
            from app.services.ai_service import generate_homecare_plan
            from app.services.sns_service import send_whatsapp

            now = datetime.now(timezone.utc)
            window_start = now - timedelta(minutes=45)
            window_end = now - timedelta(minutes=15)

            result = await db.execute(
                select(Booking).where(
                    Booking.actual_end_at >= window_start,
                    Booking.actual_end_at <= window_end,
                    Booking.status.in_(["completed", BookingStatus.COMPLETED]),
                    Booking.followup_sent == False,
                )
            )
            completed_bookings = result.scalars().all()

            for booking in completed_bookings:
                user_r = await db.execute(select(User).where(User.id == booking.customer_id))
                user = user_r.scalar_one_or_none()
                if not user or not user.phone:
                    booking.followup_sent = True
                    continue

                cp_r = await db.execute(
                    select(CustomerProfile).where(CustomerProfile.user_id == user.id)
                )
                cp = cp_r.scalar_one_or_none()

                svc_r = await db.execute(select(Service).where(Service.id == booking.service_id)) \
                    if booking.service_id else None
                svc = svc_r.scalar_one_or_none() if svc_r else None
                service_name = svc.name if svc else "your service"

                # Generate AI homecare plan
                try:
                    plan_data = await generate_homecare_plan(
                        customer_profile=cp,
                        service_name=service_name,
                        booking_id=booking.id,
                    )
                    routine = plan_data.get("routine_summary", "Follow standard aftercare for your service.")
                    next_appt = plan_data.get("next_appointment_recommendation", "In 4-6 weeks")
                except Exception:
                    routine = "Avoid washing hair for 48 hours. Use sulphate-free shampoo. Moisturise daily."
                    next_appt = "In 4-6 weeks"

                msg = HOMECARE_MESSAGE.format(
                    name=user.first_name,
                    service=service_name,
                    routine=routine,
                    next_appointment=next_appt,
                )
                await send_whatsapp(user.phone, msg)

                # Log notification
                notif = Notification(
                    id=generate_uuid(),
                    user_id=user.id,
                    notification_type="homecare_plan",
                    title=f"Your {service_name} home care plan",
                    body=msg[:300],
                    channel="whatsapp",
                    priority="normal",
                    data={"booking_id": booking.id, "service": service_name},
                )
                db.add(notif)
                booking.followup_sent = True

            await db.commit()

    return asyncio.run(_run())


@celery_app.task(name="app.tasks.homecare_tasks.send_day7_rebooking_nudge")
def send_day7_rebooking_nudge():
    """Send Day 7 re-booking nudge to customers whose booking was 7 days ago."""
    async def _run():
        async with async_session_factory() as db:
            from sqlalchemy import select, func
            from app.models.booking import Booking, BookingStatus
            from app.models.user import User
            from app.models.service import Service
            from app.models.staff import StaffProfile
            from app.services.sns_service import send_whatsapp

            today = date.today()
            seven_days_ago_start = datetime(today.year, today.month, today.day,
                                             0, 0, 0, tzinfo=timezone.utc) - timedelta(days=7)
            seven_days_ago_end = seven_days_ago_start + timedelta(days=1)

            result = await db.execute(
                select(Booking).where(
                    Booking.actual_end_at >= seven_days_ago_start,
                    Booking.actual_end_at < seven_days_ago_end,
                    Booking.status.in_(["completed", BookingStatus.COMPLETED]),
                )
            )
            week_old_bookings = result.scalars().all()

            for booking in week_old_bookings:
                user_r = await db.execute(select(User).where(User.id == booking.customer_id))
                user = user_r.scalar_one_or_none()
                if not user or not user.phone:
                    continue

                svc_r = await db.execute(select(Service).where(Service.id == booking.service_id)) \
                    if booking.service_id else None
                svc = svc_r.scalar_one_or_none() if svc_r else None
                service_name = svc.name if svc else "your last service"

                stylist_name = "your stylist"
                if booking.stylist_id:
                    staff_r = await db.execute(
                        select(StaffProfile).where(StaffProfile.id == booking.stylist_id)
                    )
                    staff = staff_r.scalar_one_or_none()
                    if staff:
                        stylist_user_r = await db.execute(
                            select(User).where(User.id == staff.user_id)
                        )
                        stylist_user = stylist_user_r.scalar_one_or_none()
                        if stylist_user:
                            stylist_name = stylist_user.first_name

                # Service-specific Day 7 tip
                SERVICE_TIPS = {
                    "hair colour": ("hair colour", "Time for a toning treatment to keep it vibrant!"),
                    "keratin": ("hair", "Avoid sulphate shampoos to maintain your smoothness."),
                    "facial": ("skin", "Your skin should be glowing! Time for a follow-up glow treatment."),
                    "manicure": ("nails", "Moisturise your cuticles daily. Ready for a fresh coat?"),
                }
                result_area, tip = "hair", "We hope you're loving your look!"
                for key, (area, service_tip) in SERVICE_TIPS.items():
                    if key in service_name.lower():
                        result_area, tip = area, service_tip
                        break

                msg = DAY7_MESSAGE.format(
                    name=user.first_name,
                    service=service_name,
                    result_area=result_area,
                    tip=tip,
                    stylist_name=stylist_name,
                )
                await send_whatsapp(user.phone, msg)

    return asyncio.run(_run())
