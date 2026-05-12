"""NPS Post-Visit Survey — WhatsApp rating request 2h after session completion."""
import asyncio
from datetime import datetime, timezone, timedelta
from app.tasks.celery_app import celery_app
from app.database import async_session_factory, generate_uuid


@celery_app.task(name="app.tasks.nps_tasks.send_nps_surveys")
def send_nps_surveys():
    """Runs every 15 min. Finds sessions completed 2h ago, sends WhatsApp NPS survey."""
    async def _run():
        async with async_session_factory() as db:
            from sqlalchemy import select
            from app.models.session import ServiceSession, SessionStatus
            from app.models.booking import Booking
            from app.models.customer import CustomerProfile
            from app.models.user import User
            from app.models.notification import Notification
            from app.services.sns_service import send_whatsapp

            now = datetime.now(timezone.utc)
            window_start = now - timedelta(hours=2, minutes=15)
            window_end = now - timedelta(hours=1, minutes=45)

            result = await db.execute(
                select(ServiceSession).where(
                    ServiceSession.completed_at >= window_start,
                    ServiceSession.completed_at <= window_end,
                    ServiceSession.status.in_(["COMPLETED", "completed"]),
                    ServiceSession.nps_sent == False,
                )
            )
            sessions = result.scalars().all()

            for session in sessions:
                try:
                    booking = await db.get(Booking, session.booking_id) if session.booking_id else None
                    if not booking:
                        continue

                    cp = await db.get(CustomerProfile, booking.customer_id) if booking.customer_id else None
                    if not cp:
                        continue

                    user = await db.get(User, cp.user_id) if cp.user_id else None
                    if not user or not user.phone:
                        continue

                    msg = (
                        f"Hi {user.first_name}! 🌟 Thank you for visiting Naturals today.\n\n"
                        f"How was your experience? Rate us 1-10:\n"
                        f"Reply with just the number — it takes 5 seconds and helps us serve you better! 💆\n\n"
                        f"9-10: Love it 💛 | 7-8: Good 😊 | 1-6: Needs work 🔧"
                    )
                    await send_whatsapp(user.phone, msg)

                    # Log notification
                    notif = Notification(
                        id=generate_uuid(),
                        user_id=user.id,
                        notification_type="nps_survey",
                        title="NPS Survey Sent",
                        body=f"NPS survey sent to {user.phone}",
                        channel="whatsapp",
                        priority="normal",
                        data={"session_id": str(session.id), "booking_id": str(session.booking_id)},
                    )
                    db.add(notif)
                    session.nps_sent = True
                except Exception:
                    continue

            await db.commit()

    return asyncio.run(_run())


@celery_app.task(name="app.tasks.nps_tasks.process_nps_reply")
def process_nps_reply(customer_phone: str, reply_text: str):
    """Process an inbound WhatsApp NPS reply. Flags detractors (≤6) for manager follow-up."""
    async def _run():
        async with async_session_factory() as db:
            from sqlalchemy import select
            from app.models.user import User
            from app.models.customer import CustomerProfile
            from app.models.booking import Booking
            from app.models.feedback import CustomerFeedback, Sentiment
            from app.models.notification import Notification
            from app.services.sns_service import send_whatsapp

            score_str = reply_text.strip().split()[0]
            try:
                score = int(score_str)
                if score < 1 or score > 10:
                    raise ValueError
            except ValueError:
                return {"status": "ignored", "reason": "not a valid score"}

            user_result = await db.execute(select(User).where(User.phone == customer_phone))
            user = user_result.scalar_one_or_none()
            if not user:
                return {"status": "ignored", "reason": "user not found"}

            # Determine sentiment
            if score >= 9:
                sentiment = "promoter"
                sentiment_enum = Sentiment.POSITIVE if hasattr(Sentiment, "POSITIVE") else "positive"
            elif score >= 7:
                sentiment = "passive"
                sentiment_enum = "neutral"
            else:
                sentiment = "detractor"
                sentiment_enum = Sentiment.NEGATIVE if hasattr(Sentiment, "NEGATIVE") else "negative"

            feedback = CustomerFeedback(
                id=generate_uuid(),
                customer_id=user.id,
                rating=score,
                sentiment=sentiment_enum,
                comment=f"NPS reply: {score}/10 ({sentiment})",
                source="whatsapp_nps",
            )
            db.add(feedback)

            # Thank the customer
            if score >= 9:
                ack = f"🌟 Thank you, {user.first_name}! We're thrilled you loved it. See you next time! 💛"
            elif score >= 7:
                ack = f"Thanks {user.first_name}! We'll keep working to make it a 10 for you next time. 😊"
            else:
                ack = f"Thank you {user.first_name} for your honest feedback. Our manager will reach out to make it right. 🙏"

            await send_whatsapp(customer_phone, ack)

            # Alert managers for detractors
            if score <= 6:
                cp_result = await db.execute(
                    select(CustomerProfile).where(CustomerProfile.user_id == user.id)
                )
                cp = cp_result.scalar_one_or_none()

                # Find latest booking to get location's manager
                if cp:
                    latest_booking_result = await db.execute(
                        select(Booking)
                        .where(Booking.customer_id == cp.id)
                        .order_by(Booking.scheduled_at.desc())
                        .limit(1)
                    )
                    booking = latest_booking_result.scalar_one_or_none()
                    if booking and booking.location_id:
                        from app.models.staff import StaffProfile
                        from app.models.user import UserRole
                        mgr_result = await db.execute(
                            select(User).join(StaffProfile, StaffProfile.user_id == User.id).where(
                                StaffProfile.location_id == booking.location_id,
                                User.role.in_([UserRole.SALON_MANAGER, "salon_manager"]),
                            ).limit(1)
                        )
                        mgr = mgr_result.scalar_one_or_none()
                        if mgr and mgr.phone:
                            mgr_msg = (
                                f"⚠️ NPS Alert — {user.first_name} {user.last_name} rated {score}/10.\n"
                                f"Please reach out to resolve their concern within 24h."
                            )
                            await send_whatsapp(mgr.phone, mgr_msg)

                        notif = Notification(
                            id=generate_uuid(),
                            user_id=booking.location_id,
                            notification_type="nps_detractor",
                            title=f"NPS Detractor: {score}/10",
                            body=f"{user.first_name} {user.last_name} rated {score}/10. Follow up required.",
                            channel="whatsapp",
                            priority="high",
                            data={"customer_id": str(user.id), "score": score},
                        )
                        db.add(notif)

            await db.commit()
            return {"status": "processed", "score": score, "sentiment": sentiment}

    return asyncio.run(_run())
