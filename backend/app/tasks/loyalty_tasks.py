"""Loyalty Tasks — Feature 12: AuraPOINTS birthday reminders + tier upgrades.

Beat schedule:
- Birthday reminders: Daily at 9:00 AM IST
- Tier upgrade check: Daily at midnight IST
- Re-engagement (30-day no-visit): Daily at 10:00 AM IST
"""
import asyncio
from datetime import datetime, timezone, timedelta, date
from app.tasks.celery_app import celery_app
from app.database import async_session_factory, generate_uuid


TIER_THRESHOLDS = {
    "silver": 5,
    "gold": 10,
    "platinum": 20,
}

BIRTHDAY_MESSAGE = (
    "🎂 Happy Birthday {name}! Your special day deserves a special treat. "
    "Enjoy DOUBLE AuraPOINTS on any service this month + a complimentary head massage. "
    "Book now: {booking_url}"
)

RE_ENGAGEMENT_MESSAGE = (
    "Hi {name}, we miss you! 💕 It's been {days} days since your last visit. "
    "Your favourite stylist {stylist_name} is available this weekend. "
    "Book your spot: {booking_url}"
)

TIER_UPGRADE_MESSAGE = (
    "Congratulations {name}! 🌟 You've been upgraded to {tier} tier at AURA. "
    "Enjoy exclusive {tier} benefits from today. "
    "Check your rewards: {booking_url}"
)


@celery_app.task(name="app.tasks.loyalty_tasks.send_birthday_reminders")
def send_birthday_reminders():
    """Send birthday WhatsApp messages 7 days before each customer's birthday.
    Also sends double-points offer on the birthday month start.
    """
    async def _run():
        async with async_session_factory() as db:
            from sqlalchemy import select, extract
            from app.models.user import User
            from app.models.loyalty import LoyaltyProgram
            from app.services.sns_service import send_whatsapp

            today = date.today()
            # Target: birthday is exactly 7 days from now
            target_date = today + timedelta(days=7)

            result = await db.execute(
                select(User).where(
                    User.is_active == True,
                    User.birth_date.isnot(None),
                    extract("month", User.birth_date) == target_date.month,
                    extract("day", User.birth_date) == target_date.day,
                )
            )
            birthday_users = result.scalars().all()

            for user in birthday_users:
                if not user.phone:
                    continue

                msg = BIRTHDAY_MESSAGE.format(
                    name=user.first_name,
                    booking_url="https://natural.dhilip.in/app/book",
                )
                await send_whatsapp(user.phone, msg)

                # Create a loyalty notification record
                from app.models.notification import Notification
                notif = Notification(
                    id=generate_uuid(),
                    user_id=user.id,
                    notification_type="birthday_offer",
                    title=f"Happy Birthday {user.first_name}!",
                    body=msg,
                    channel="whatsapp",
                    priority="normal",
                    data={"birthday": str(user.birth_date), "offer": "double_points"},
                )
                db.add(notif)

            await db.commit()

    return asyncio.run(_run())


@celery_app.task(name="app.tasks.loyalty_tasks.check_tier_upgrades")
def check_tier_upgrades():
    """Check all loyalty programs and upgrade tiers when visit thresholds are crossed."""
    async def _run():
        async with async_session_factory() as db:
            from sqlalchemy import select
            from app.models.loyalty import LoyaltyProgram
            from app.models.user import User
            from app.services.sns_service import send_whatsapp

            result = await db.execute(select(LoyaltyProgram))
            programs = result.scalars().all()

            for program in programs:
                # Determine expected tier from lifetime visits
                visits = getattr(program, "total_visits_used", 0) or 0
                current_tier = (program.tier or "bronze").lower()

                new_tier = current_tier
                if visits >= TIER_THRESHOLDS["platinum"]:
                    new_tier = "platinum"
                elif visits >= TIER_THRESHOLDS["gold"]:
                    new_tier = "gold"
                elif visits >= TIER_THRESHOLDS["silver"]:
                    new_tier = "silver"

                if new_tier != current_tier:
                    program.tier = new_tier

                    user_result = await db.execute(
                        select(User).where(User.id == program.customer_id)
                    )
                    user = user_result.scalar_one_or_none()
                    if user and user.phone:
                        msg = TIER_UPGRADE_MESSAGE.format(
                            name=user.first_name,
                            tier=new_tier.title(),
                            booking_url="https://natural.dhilip.in/app/profile",
                        )
                        await send_whatsapp(user.phone, msg)

            await db.commit()

    return asyncio.run(_run())


@celery_app.task(name="app.tasks.loyalty_tasks.send_re_engagement")
def send_re_engagement():
    """Send re-engagement WhatsApp to customers who haven't visited in 30+ days."""
    async def _run():
        async with async_session_factory() as db:
            from sqlalchemy import select
            from app.models.customer import CustomerProfile
            from app.models.user import User
            from app.models.staff import StaffProfile
            from app.services.sns_service import send_whatsapp

            cutoff = date.today() - timedelta(days=30)

            result = await db.execute(
                select(CustomerProfile).where(
                    CustomerProfile.last_visit_date.isnot(None),
                    CustomerProfile.last_visit_date <= cutoff,
                )
            )
            inactive_customers = result.scalars().all()

            for cp in inactive_customers:
                user_r = await db.execute(select(User).where(User.id == cp.user_id))
                user = user_r.scalar_one_or_none()
                if not user or not user.phone:
                    continue

                # Find preferred stylist name
                stylist_name = "our team"
                if cp.preferred_stylist_id:
                    stylist_r = await db.execute(
                        select(StaffProfile).where(StaffProfile.id == cp.preferred_stylist_id)
                    )
                    stylist = stylist_r.scalar_one_or_none()
                    if stylist:
                        stylist_user_r = await db.execute(
                            select(User).where(User.id == stylist.user_id)
                        )
                        stylist_user = stylist_user_r.scalar_one_or_none()
                        if stylist_user:
                            stylist_name = stylist_user.first_name

                days_away = (date.today() - cp.last_visit_date).days
                msg = RE_ENGAGEMENT_MESSAGE.format(
                    name=user.first_name,
                    days=days_away,
                    stylist_name=stylist_name,
                    booking_url="https://natural.dhilip.in/app/book",
                )
                await send_whatsapp(user.phone, msg)

            await db.commit()

    return asyncio.run(_run())
