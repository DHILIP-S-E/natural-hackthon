"""Track 5: Customer Experience — 10 agents for personalized, transparent,
emotionally intelligent salon experiences (PS-05.01 through PS-05.10)."""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, func, case, and_, or_, update, literal
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, generate_uuid, enum_val
from app.dependencies import get_current_user, require_role
from app.models import (
    User, Location, StaffProfile, CustomerProfile,
    Service, SOP, Booking, BookingStatus, ServiceSession, SessionStatus,
    SmartQueueEntry, QueueStatus, CustomerFeedback, Sentiment,
    QualityAssessment, Notification, NotificationChannel, NotificationPriority,
    TrainingRecord, SkillAssessment,
)
from app.models.handover import ClientHandover, StylistCustomerMemory
from app.models.followup import FollowUpSequence
from app.models.waiting_experience import WaitingExperience, AmbientControl
from app.models.loyalty import LoyaltyProgram, LoyaltyTransaction
from app.models.recommendation import ServiceRecommendation
from app.models.inventory import InventoryItem
from app.models.homecare import HomecarePlan
from app.schemas.common import APIResponse
from app.agents import AgentAction, register_agent


# ═══════════════════════════════════════════════════════════════════════════════
# 44. waiting_engagement (PS-05.01)
# ═══════════════════════════════════════════════════════════════════════════════

class WaitingEngagementRequest(BaseModel):
    customer_id: str
    location_id: str


async def waiting_engagement_handler(
    body: WaitingEngagementRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["customer", "stylist", "salon_manager"])),
):
    """Personalized waiting experience: activities, pre-consultation, trending services."""
    customer_id = body.customer_id
    location_id = body.location_id

    # Fetch customer profile
    cp_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.id == customer_id)
    )
    customer = cp_result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Get current queue entry for estimated wait
    queue_result = await db.execute(
        select(SmartQueueEntry).where(
            SmartQueueEntry.customer_id == customer_id,
            SmartQueueEntry.location_id == location_id,
            SmartQueueEntry.status == QueueStatus.WAITING,
        ).order_by(SmartQueueEntry.created_at.desc()).limit(1)
    )
    queue_entry = queue_result.scalar_one_or_none()
    estimated_wait_mins = queue_entry.estimated_wait_mins if queue_entry else 15

    # Build activity suggestions based on profile completeness and features
    activities = []

    # Suggest completing profile if low completeness
    if not customer.passport_completeness or customer.passport_completeness < 70:
        activities.append({
            "type": "complete_profile",
            "prompt": "Complete your beauty passport for a more personalized experience!",
            "url": "/profile/beauty-passport",
        })

    # Suggest AR try-on if location has smart mirrors
    loc_result = await db.execute(
        select(Location).where(Location.id == location_id)
    )
    location = loc_result.scalar_one_or_none()
    if location and location.smart_mirror_enabled:
        activities.append({
            "type": "ar_tryon",
            "prompt": "Try new looks on our AR Smart Mirror while you wait!",
            "url": "/ar-mirror/start",
        })

    # Suggest SOULSKIN quiz if no dominant archetype
    if not customer.dominant_archetype:
        activities.append({
            "type": "soulskin_quiz",
            "prompt": "Discover your SOULSKIN archetype for a soul-aligned experience.",
            "url": "/soulskin/quiz",
        })

    # Always suggest browsing trends
    activities.append({
        "type": "browse_trends",
        "prompt": "Explore what's trending in beauty right now!",
        "url": "/trends/explore",
    })

    # Pre-consultation questions to save stylist time
    pre_consultation_questions = []
    if not customer.known_allergies:
        pre_consultation_questions.append(
            "Do you have any known allergies to hair or skin products?"
        )
    if not customer.primary_goal:
        pre_consultation_questions.append(
            "What's the main beauty goal you'd like to achieve today?"
        )
    if not customer.hair_type:
        pre_consultation_questions.append(
            "How would you describe your hair type? (straight, wavy, curly, coily)"
        )
    if customer.last_color_date:
        pre_consultation_questions.append(
            "Have you had any chemical treatments since your last visit?"
        )
    else:
        pre_consultation_questions.append(
            "Have you had any chemical hair treatments (color, keratin, perm) recently?"
        )

    # Trending services at this location
    now = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)
    trending_result = await db.execute(
        select(
            Service.id,
            Service.name,
            Service.category,
            Service.short_description,
            func.count(Booking.id).label("booking_count"),
        )
        .join(Booking, Booking.service_id == Service.id)
        .where(
            Booking.location_id == location_id,
            Booking.created_at >= thirty_days_ago,
            Booking.status != BookingStatus.CANCELLED,
            Service.is_active == True,
        )
        .group_by(Service.id, Service.name, Service.category, Service.short_description)
        .order_by(func.count(Booking.id).desc())
        .limit(5)
    )
    trending_services = [
        {
            "service_id": row.id,
            "name": row.name,
            "category": row.category,
            "description": row.short_description,
            "popularity_count": row.booking_count,
        }
        for row in trending_result.all()
    ]

    # Record the waiting experience
    experience = WaitingExperience(
        id=generate_uuid(),
        customer_id=customer_id,
        location_id=location_id,
        queue_entry_id=queue_entry.id if queue_entry else None,
        experience_type="personalized_engagement",
        content_served={
            "activities_offered": [a["type"] for a in activities],
            "pre_consultation_count": len(pre_consultation_questions),
            "trending_services_count": len(trending_services),
        },
        started_at=now,
    )
    db.add(experience)

    return APIResponse(
        success=True,
        data={
            "estimated_wait_mins": estimated_wait_mins,
            "activities": activities,
            "pre_consultation_questions": pre_consultation_questions,
            "trending_services_to_explore": trending_services,
        },
    )


agent_waiting_engagement = register_agent(AgentAction(
    name="waiting_engagement",
    description="Personalized waiting experience with activities, pre-consultation questions, and trending services",
    track="experience",
    feature="waiting",
    method="post",
    path="/agents/track5/waiting/engage",
    handler=waiting_engagement_handler,
    roles=["customer", "stylist", "salon_manager"],
    ps_codes=["PS-05.01"],
))


# ═══════════════════════════════════════════════════════════════════════════════
# 45. smart_followup_generate (PS-05.02)
# ═══════════════════════════════════════════════════════════════════════════════

class SmartFollowupRequest(BaseModel):
    booking_id: str


async def smart_followup_generate_handler(
    body: SmartFollowupRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager"])),
):
    """Generate personalized follow-up schedule after completed booking."""
    booking_id = body.booking_id

    # Get booking with service details
    booking_result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = booking_result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.status != BookingStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Booking must be completed to generate follow-up")

    # Get service for interval info
    service_result = await db.execute(
        select(Service).where(Service.id == booking.service_id)
    )
    service = service_result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # Get customer profile
    cp_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.id == booking.customer_id)
    )
    customer = cp_result.scalar_one_or_none()

    # Determine rebooking interval based on service category
    category = (service.category or "").lower()
    rebooking_intervals = {
        "haircut": 30,
        "hair color": 42,
        "colour": 42,
        "color": 42,
        "facial": 28,
        "skin treatment": 21,
        "spa": 30,
        "keratin": 90,
        "smoothening": 90,
        "manicure": 14,
        "pedicure": 14,
        "threading": 14,
        "waxing": 21,
        "bridal": 60,
        "makeup": 60,
    }
    service_interval = rebooking_intervals.get(category, 30)

    # Get customer preferred language for message personalization
    cust_user_result = await db.execute(
        select(User).where(User.id == customer.user_id) if customer else select(User).where(User.id == None)
    )
    cust_user = cust_user_result.scalar_one_or_none()
    customer_name = cust_user.first_name if cust_user else "Valued Customer"

    # Build follow-up schedule
    schedule = [
        {
            "day_after": 1,
            "channel": "whatsapp",
            "message": (
                f"Hi {customer_name}! How are you enjoying your {service.name}? "
                f"We'd love to hear how you're feeling about the results!"
            ),
            "purpose": "check_in",
        },
        {
            "day_after": 3,
            "channel": "whatsapp",
            "message": (
                f"Hi {customer_name}, quick reminder for your {service.name} home care: "
                f"follow the routine shared by your stylist for best results. "
                f"Need product recommendations? Reply here!"
            ),
            "purpose": "home_care_reminder",
        },
    ]

    # If chemical service, add day 7 safety check
    if service.is_chemical:
        schedule.append({
            "day_after": 7,
            "channel": "whatsapp",
            "message": (
                f"Hi {customer_name}, it's been a week since your {service.name}. "
                f"How is your hair/skin feeling? Any concerns? We're here to help!"
            ),
            "purpose": "check_in",
        })

    # Rebooking nudge at the appropriate interval
    schedule.append({
        "day_after": service_interval - 5,
        "channel": "push",
        "message": (
            f"Hi {customer_name}, it's almost time for your next {service.name}! "
            f"Book now to keep your look fresh. Tap to see available slots."
        ),
        "purpose": "rebooking_nudge",
    })

    # Save the follow-up sequence
    followup = FollowUpSequence(
        id=generate_uuid(),
        booking_id=booking_id,
        customer_id=booking.customer_id,
        location_id=booking.location_id,
        sequence_type="smart_followup",
        status="active",
        steps={"schedule": schedule},
        started_at=datetime.now(timezone.utc),
    )
    db.add(followup)

    return APIResponse(
        success=True,
        data={
            "booking_id": booking_id,
            "service_name": service.name,
            "service_category": service.category,
            "service_interval_days": service_interval,
            "followup_schedule": schedule,
        },
    )


agent_smart_followup = register_agent(AgentAction(
    name="smart_followup_generate",
    description="Generate personalized post-service follow-up schedule based on service type and customer profile",
    track="experience",
    feature="followup",
    method="post",
    path="/agents/track5/followup/generate",
    handler=smart_followup_generate_handler,
    roles=["stylist", "salon_manager"],
    ps_codes=["PS-05.02"],
))


# ═══════════════════════════════════════════════════════════════════════════════
# 46. rapport_handover (PS-05.03)
# ═══════════════════════════════════════════════════════════════════════════════

async def rapport_handover_handler(
    customer_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager"])),
):
    """Compile relationship notes, conversation preferences, and important dates for a customer."""

    # Verify customer exists
    cp_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.id == customer_id)
    )
    customer = cp_result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Get customer user info
    cust_user_result = await db.execute(
        select(User).where(User.id == customer.user_id)
    )
    cust_user = cust_user_result.scalar_one_or_none()

    # Collect all stylist memory entries for this customer
    memories_result = await db.execute(
        select(StylistCustomerMemory).where(
            StylistCustomerMemory.customer_id == customer_id
        ).order_by(StylistCustomerMemory.created_at.desc())
    )
    memories = memories_result.scalars().all()

    # Categorize memories
    personal_notes = []
    conversation_preferences = None
    important_dates = []
    do_not_mention = []
    for mem in memories:
        if mem.memory_type == "personal_note":
            personal_notes.append(mem.content)
        elif mem.memory_type == "conversation_preference":
            conversation_preferences = mem.content
        elif mem.memory_type == "important_date":
            important_dates.append(mem.content)
        elif mem.memory_type == "do_not_mention":
            do_not_mention.append(mem.content)

    # If no explicit conversation preference, infer from feedback
    if not conversation_preferences:
        feedback_count_result = await db.execute(
            select(func.count(CustomerFeedback.id)).where(
                CustomerFeedback.customer_id == customer_id,
                CustomerFeedback.comment != None,
            )
        )
        comment_count = feedback_count_result.scalar() or 0
        total_fb_result = await db.execute(
            select(func.count(CustomerFeedback.id)).where(
                CustomerFeedback.customer_id == customer_id
            )
        )
        total_fb = total_fb_result.scalar() or 1
        if comment_count / max(total_fb, 1) > 0.6:
            conversation_preferences = "chatty"
        else:
            conversation_preferences = "focused"

    # Favorite services — most booked
    fav_result = await db.execute(
        select(Service.name, func.count(Booking.id).label("cnt"))
        .join(Booking, Booking.service_id == Service.id)
        .where(Booking.customer_id == customer_id, Booking.status == BookingStatus.COMPLETED)
        .group_by(Service.name)
        .order_by(func.count(Booking.id).desc())
        .limit(5)
    )
    favorite_services = [{"service": row.name, "times_booked": row.cnt} for row in fav_result.all()]

    # Communication style from customer profile
    communication_style = customer.emotional_sensitivity or "standard"

    # Stylist notes history from completed sessions
    notes_result = await db.execute(
        select(
            ServiceSession.stylist_notes,
            Booking.scheduled_at,
            StaffProfile.id.label("stylist_id"),
        )
        .join(Booking, Booking.id == ServiceSession.booking_id)
        .outerjoin(StaffProfile, StaffProfile.id == Booking.stylist_id)
        .where(
            Booking.customer_id == customer_id,
            ServiceSession.stylist_notes != None,
        )
        .order_by(Booking.scheduled_at.desc())
        .limit(10)
    )
    stylist_notes_history = [
        {
            "date": str(row.scheduled_at),
            "stylist_id": row.stylist_id,
            "note": row.stylist_notes,
        }
        for row in notes_result.all()
    ]

    # Handover records
    handover_result = await db.execute(
        select(ClientHandover).where(
            ClientHandover.customer_id == customer_id
        ).order_by(ClientHandover.created_at.desc()).limit(5)
    )
    handovers = handover_result.scalars().all()

    # Build important dates list with upcoming events from profile
    if customer.upcoming_events:
        for event in customer.upcoming_events:
            important_dates.append(event)

    return APIResponse(
        success=True,
        data={
            "customer_id": customer_id,
            "customer_name": f"{cust_user.first_name} {cust_user.last_name}" if cust_user else None,
            "personal_notes": personal_notes[:20],
            "conversation_preferences": conversation_preferences,
            "important_dates": important_dates,
            "favorite_services": favorite_services,
            "communication_style": communication_style,
            "preferred_touch_pressure": customer.preferred_touch_pressure,
            "dominant_archetype": customer.dominant_archetype,
            "stylist_notes_history": stylist_notes_history,
            "do_not_mention": do_not_mention,
            "total_visits": customer.total_visits,
            "last_visit_date": str(customer.last_visit_date) if customer.last_visit_date else None,
            "recent_handovers": [
                {
                    "from_stylist_id": h.from_stylist_id,
                    "to_stylist_id": h.to_stylist_id,
                    "reason": h.reason,
                    "relationship_notes": h.relationship_notes,
                    "conversation_style": h.conversation_style,
                }
                for h in handovers
            ],
        },
    )


agent_rapport_handover = register_agent(AgentAction(
    name="rapport_handover",
    description="Compile relationship notes, preferences, and history for stylist handover or preparation",
    track="experience",
    feature="rapport",
    method="get",
    path="/agents/track5/rapport/handover",
    handler=rapport_handover_handler,
    roles=["stylist", "salon_manager"],
    ps_codes=["PS-05.03"],
))


# ═══════════════════════════════════════════════════════════════════════════════
# 47. service_transparency_feed (PS-05.04)
# ═══════════════════════════════════════════════════════════════════════════════

async def service_transparency_feed_handler(
    session_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["customer", "stylist", "salon_manager"])),
):
    """Real-time transparency data for customer display during service."""

    # Get session with booking and SOP
    session_result = await db.execute(
        select(ServiceSession).where(ServiceSession.id == session_id)
    )
    session = session_result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get booking for service info
    booking_result = await db.execute(
        select(Booking).where(Booking.id == session.booking_id)
    )
    booking = booking_result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Get service
    service_result = await db.execute(
        select(Service).where(Service.id == booking.service_id)
    )
    service = service_result.scalar_one_or_none()

    # Get SOP for step details
    sop = None
    if session.sop_id:
        sop_result = await db.execute(
            select(SOP).where(SOP.id == session.sop_id)
        )
        sop = sop_result.scalar_one_or_none()

    # Parse current step info from SOP
    current_step_name = "In Progress"
    current_step_description = ""
    steps_total = session.steps_total or 1
    steps_completed_list = session.steps_completed or []
    steps_completed_count = len(steps_completed_list)
    current_step_num = session.current_step or 1

    if sop and sop.steps:
        sop_steps = sop.steps if isinstance(sop.steps, list) else sop.steps.get("steps", [])
        if isinstance(sop_steps, list) and 0 < current_step_num <= len(sop_steps):
            step_data = sop_steps[current_step_num - 1]
            if isinstance(step_data, dict):
                current_step_name = step_data.get("name", f"Step {current_step_num}")
                current_step_description = step_data.get("description", "")

    # Products being used
    products_being_used = []
    if session.products_used:
        products_data = session.products_used
        if isinstance(products_data, list):
            for p in products_data:
                if isinstance(p, dict):
                    products_being_used.append({
                        "name": p.get("name", "Unknown"),
                        "purpose": p.get("purpose", ""),
                        "safety_info": p.get("safety_info", "Dermatologically tested"),
                    })
        elif isinstance(products_data, dict):
            for name, details in products_data.items():
                products_being_used.append({
                    "name": name,
                    "purpose": details.get("purpose", "") if isinstance(details, dict) else str(details),
                    "safety_info": details.get("safety_info", "Dermatologically tested") if isinstance(details, dict) else "Dermatologically tested",
                })

    # Calculate time remaining
    time_remaining_mins = None
    if session.started_at and service:
        started = session.started_at if isinstance(session.started_at, datetime) else datetime.fromisoformat(str(session.started_at))
        elapsed = (datetime.now(timezone.utc) - started.replace(tzinfo=timezone.utc) if started.tzinfo is None else datetime.now(timezone.utc) - started).total_seconds() / 60
        total_duration = service.duration_minutes or 60
        time_remaining_mins = max(0, int(total_duration - elapsed))

    # Expected outcome
    expected_outcome = service.description or f"Professional {service.name} service"

    return APIResponse(
        success=True,
        data={
            "session_id": session_id,
            "service_name": service.name if service else "Unknown",
            "current_step_name": current_step_name,
            "current_step_description": current_step_description,
            "current_step_number": current_step_num,
            "products_being_used": products_being_used,
            "time_remaining_mins": time_remaining_mins,
            "steps_completed": steps_completed_count,
            "steps_total": steps_total,
            "expected_outcome_description": expected_outcome,
            "status": enum_val(session.status) if session.status else "active",
        },
    )


agent_service_transparency = register_agent(AgentAction(
    name="service_transparency_feed",
    description="Real-time transparency data for customer display during active service session",
    track="experience",
    feature="transparency",
    method="get",
    path="/agents/track5/transparency/feed",
    handler=service_transparency_feed_handler,
    roles=["customer", "stylist", "salon_manager"],
    ps_codes=["PS-05.04"],
))


# ═══════════════════════════════════════════════════════════════════════════════
# 48. realtime_micro_feedback (PS-05.05)
# ═══════════════════════════════════════════════════════════════════════════════

class MicroFeedbackRequest(BaseModel):
    session_id: str
    feedback_type: str = Field(..., pattern="^(comfort|satisfaction|concern)$")
    value: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


async def realtime_micro_feedback_handler(
    body: MicroFeedbackRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["customer", "stylist", "salon_manager"])),
):
    """Record in-service micro-feedback and escalate if low score."""
    session_id = body.session_id

    # Get session
    session_result = await db.execute(
        select(ServiceSession).where(ServiceSession.id == session_id)
    )
    session = session_result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status != SessionStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Session is not currently active")

    # Build feedback entry
    now = datetime.now(timezone.utc)
    feedback_entry = {
        "timestamp": now.isoformat(),
        "type": body.feedback_type,
        "value": body.value,
        "comment": body.comment,
        "recorded_by": user.id,
    }

    # Append to session's in_service_feedback JSONB
    existing_feedback = session.in_service_feedback or {"entries": []}
    if isinstance(existing_feedback, list):
        existing_feedback = {"entries": existing_feedback}
    existing_feedback.setdefault("entries", []).append(feedback_entry)
    session.in_service_feedback = existing_feedback

    # Update comfort level if feedback_type is comfort
    if body.feedback_type == "comfort":
        session.comfort_level = body.value

    # Escalation logic: if value <= 2, alert manager
    escalated = False
    if body.value <= 2:
        escalated = True
        # Get booking to find location manager
        booking_result = await db.execute(
            select(Booking).where(Booking.id == session.booking_id)
        )
        booking = booking_result.scalar_one_or_none()

        if booking:
            # Find location manager
            loc_result = await db.execute(
                select(Location).where(Location.id == booking.location_id)
            )
            location = loc_result.scalar_one_or_none()

            if location and location.manager_id:
                alert = Notification(
                    id=generate_uuid(),
                    user_id=location.manager_id,
                    notification_type="micro_feedback_alert",
                    title="Low In-Service Feedback Alert",
                    body=(
                        f"Customer gave {body.feedback_type} rating of {body.value}/5 "
                        f"during active session {session_id}. "
                        f"Comment: {body.comment or 'None'}"
                    ),
                    data={
                        "session_id": session_id,
                        "booking_id": session.booking_id,
                        "feedback_type": body.feedback_type,
                        "value": body.value,
                    },
                    channel=NotificationChannel.PUSH,
                    priority=NotificationPriority.URGENT,
                    sent_at=now,
                )
                db.add(alert)

    return APIResponse(
        success=True,
        data={
            "recorded": True,
            "escalated": escalated,
            "feedback_type": body.feedback_type,
            "value": body.value,
        },
    )


agent_micro_feedback = register_agent(AgentAction(
    name="realtime_micro_feedback",
    description="Record real-time micro-feedback during service session, auto-escalate low scores",
    track="experience",
    feature="feedback",
    method="post",
    path="/agents/track5/feedback/micro",
    handler=realtime_micro_feedback_handler,
    roles=["customer", "stylist", "salon_manager"],
    ps_codes=["PS-05.05"],
))


# ═══════════════════════════════════════════════════════════════════════════════
# 49. language_service_brief (PS-05.06)
# ═══════════════════════════════════════════════════════════════════════════════

class LanguageServiceBriefRequest(BaseModel):
    customer_id: str
    stylist_id: str
    service_id: str


async def language_service_brief_handler(
    body: LanguageServiceBriefRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager"])),
):
    """Check language compatibility and generate simplified bilingual service brief."""

    # Get customer's preferred language
    cp_result = await db.execute(
        select(CustomerProfile, User).join(User, User.id == CustomerProfile.user_id)
        .where(CustomerProfile.id == body.customer_id)
    )
    row = cp_result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Customer not found")
    customer, cust_user = row

    customer_language = cust_user.preferred_language or "en"

    # Get stylist languages
    staff_result = await db.execute(
        select(StaffProfile).where(StaffProfile.id == body.stylist_id)
    )
    stylist = staff_result.scalar_one_or_none()
    if not stylist:
        raise HTTPException(status_code=404, detail="Stylist not found")

    stylist_languages = stylist.languages_spoken or ["en"]

    # Get service + SOP
    svc_result = await db.execute(
        select(Service).where(Service.id == body.service_id)
    )
    service = svc_result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    sop = None
    if service.sop_id:
        sop_result = await db.execute(
            select(SOP).where(SOP.id == service.sop_id)
        )
        sop = sop_result.scalar_one_or_none()

    # Check for language mismatch
    language_match = customer_language in stylist_languages

    # Build simplified service steps from SOP
    service_steps_simplified = []
    if sop and sop.steps:
        sop_steps = sop.steps if isinstance(sop.steps, list) else sop.steps.get("steps", [])
        if isinstance(sop_steps, list):
            for i, step in enumerate(sop_steps, 1):
                if isinstance(step, dict):
                    service_steps_simplified.append({
                        "step_number": i,
                        "name": step.get("name", f"Step {i}"),
                        "description": step.get("description", ""),
                        "duration_mins": step.get("duration_minutes", None),
                    })

    if not service_steps_simplified:
        service_steps_simplified = [
            {"step_number": 1, "name": "Consultation", "description": "Discuss desired outcome", "duration_mins": 5},
            {"step_number": 2, "name": "Service", "description": service.name, "duration_mins": service.duration_minutes - 10},
            {"step_number": 3, "name": "Finishing", "description": "Final touches and styling", "duration_mins": 5},
        ]

    # Key terms that may need translation in salon context
    key_terms = [
        {"term": "consultation", "context": "Initial discussion about what you want"},
        {"term": "processing time", "context": "Time for chemical treatment to work"},
        {"term": "rinse", "context": "Washing out product with water"},
        {"term": "trim", "context": "Cutting a small amount of hair"},
        {"term": "deep conditioning", "context": "Intensive moisture treatment"},
        {"term": "patch test", "context": "Small skin test for allergic reactions"},
        {"term": "blow dry", "context": "Drying hair with a dryer"},
        {"term": "allergies", "context": "Products that cause skin reactions"},
    ]

    # Communication tips for language barrier
    communication_tips = []
    if not language_match:
        communication_tips = [
            "Use visual references (photos on phone/tablet) to confirm desired outcome",
            "Demonstrate each step with gestures before proceeding",
            "Use mirror to point and confirm length/style",
            "Keep sentences short and use simple words",
            "Check understanding frequently with thumbs up/down gestures",
            "Have the translation of key safety warnings ready",
        ]
    else:
        communication_tips = [
            f"Both speak {customer_language} — direct communication should be seamless",
        ]

    return APIResponse(
        success=True,
        data={
            "language_match": language_match,
            "customer_language": customer_language,
            "stylist_languages": stylist_languages,
            "service_name": service.name,
            "service_steps_simplified": service_steps_simplified,
            "key_terms_translated": key_terms,
            "communication_tips": communication_tips,
            "service_duration_minutes": service.duration_minutes,
            "is_chemical_service": service.is_chemical,
        },
    )


agent_language_brief = register_agent(AgentAction(
    name="language_service_brief",
    description="Check language compatibility and generate bilingual service brief for stylist-customer communication",
    track="experience",
    feature="language",
    method="post",
    path="/agents/track5/language/brief",
    handler=language_service_brief_handler,
    roles=["stylist", "salon_manager"],
    ps_codes=["PS-05.06"],
))


# ═══════════════════════════════════════════════════════════════════════════════
# 50. no_show_recovery (PS-05.07)
# ═══════════════════════════════════════════════════════════════════════════════

class NoShowRecoveryRequest(BaseModel):
    booking_id: str


async def no_show_recovery_handler(
    body: NoShowRecoveryRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager"])),
):
    """Mark booking as no-show, promote waitlist entry, send re-engagement."""
    booking_id = body.booking_id

    # Get booking
    booking_result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = booking_result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.status == BookingStatus.NO_SHOW:
        raise HTTPException(status_code=400, detail="Booking already marked as no-show")

    now = datetime.now(timezone.utc)

    # Mark booking as no-show
    booking.status = BookingStatus.NO_SHOW

    # Check queue waitlist for same location + similar time window
    slot_recovered = False
    waitlist_customer_promoted = None

    waitlist_result = await db.execute(
        select(SmartQueueEntry).where(
            SmartQueueEntry.location_id == booking.location_id,
            SmartQueueEntry.is_waitlist == True,
            SmartQueueEntry.status == QueueStatus.WAITING,
        ).order_by(SmartQueueEntry.joined_queue_at.asc()).limit(1)
    )
    waitlist_entry = waitlist_result.scalar_one_or_none()

    if waitlist_entry:
        # Promote the waitlist customer
        waitlist_entry.status = QueueStatus.ASSIGNED
        waitlist_entry.promoted_from_waitlist = True
        waitlist_entry.assigned_at = now

        # Create a new booking for the promoted customer
        new_booking = Booking(
            id=generate_uuid(),
            customer_id=waitlist_entry.customer_id,
            location_id=booking.location_id,
            stylist_id=booking.stylist_id,
            service_id=waitlist_entry.service_id or booking.service_id,
            status=BookingStatus.CONFIRMED,
            scheduled_at=booking.scheduled_at,
            base_price=booking.base_price,
            source=BookingStatus.CONFIRMED and "queue",
            queue_entry_id=waitlist_entry.id,
        )
        db.add(new_booking)

        slot_recovered = True
        waitlist_customer_promoted = waitlist_entry.customer_id

        # Notify the waitlist customer
        if waitlist_entry.customer_id:
            # Get the customer's user_id for notification
            promoted_cp_result = await db.execute(
                select(CustomerProfile).where(CustomerProfile.id == waitlist_entry.customer_id)
            )
            promoted_cp = promoted_cp_result.scalar_one_or_none()
            if promoted_cp:
                promo_notification = Notification(
                    id=generate_uuid(),
                    user_id=promoted_cp.user_id,
                    notification_type="waitlist_promotion",
                    title="Your Slot is Ready!",
                    body="Great news! A slot has opened up for you. Your appointment is confirmed.",
                    data={"booking_id": new_booking.id},
                    channel=NotificationChannel.PUSH,
                    priority=NotificationPriority.HIGH,
                    sent_at=now,
                )
                db.add(promo_notification)

    # Send re-engagement notification to the no-show customer
    re_engagement_sent = False
    noshow_cp_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.id == booking.customer_id)
    )
    noshow_cp = noshow_cp_result.scalar_one_or_none()
    if noshow_cp:
        noshow_user_result = await db.execute(
            select(User).where(User.id == noshow_cp.user_id)
        )
        noshow_user = noshow_user_result.scalar_one_or_none()
        customer_name = noshow_user.first_name if noshow_user else "there"

        re_engage = Notification(
            id=generate_uuid(),
            user_id=noshow_cp.user_id,
            notification_type="no_show_recovery",
            title="We Missed You!",
            body=(
                f"Hi {customer_name}, we noticed you couldn't make it to your appointment today. "
                f"No worries! Would you like to reschedule? We'd love to see you."
            ),
            data={"original_booking_id": booking_id},
            channel=NotificationChannel.WHATSAPP,
            priority=NotificationPriority.NORMAL,
            sent_at=now,
        )
        db.add(re_engage)
        re_engagement_sent = True

    return APIResponse(
        success=True,
        data={
            "booking_id": booking_id,
            "slot_recovered": slot_recovered,
            "waitlist_customer_promoted": waitlist_customer_promoted,
            "re_engagement_sent": re_engagement_sent,
        },
    )


agent_no_show_recovery = register_agent(AgentAction(
    name="no_show_recovery",
    description="Mark booking as no-show, promote waitlist entry, and send re-engagement notification",
    track="experience",
    feature="no_show",
    method="post",
    path="/agents/track5/noshow/recover",
    handler=no_show_recovery_handler,
    roles=["stylist", "salon_manager"],
    ps_codes=["PS-05.07"],
))


# ═══════════════════════════════════════════════════════════════════════════════
# 51. stylist_performance_360 (PS-05.08)
# ═══════════════════════════════════════════════════════════════════════════════

async def stylist_performance_360_handler(
    staff_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager", "franchise_owner", "regional_manager"])),
):
    """Multi-dimensional 360-degree performance view for a stylist."""
    now = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)
    sixty_days_ago = now - timedelta(days=60)

    # Verify staff exists
    staff_result = await db.execute(
        select(StaffProfile).where(StaffProfile.id == staff_id)
    )
    staff = staff_result.scalar_one_or_none()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    # Services completed in last 30 days
    completed_result = await db.execute(
        select(func.count(Booking.id)).where(
            Booking.stylist_id == staff_id,
            Booking.status == BookingStatus.COMPLETED,
            Booking.actual_end_at >= thirty_days_ago,
        )
    )
    services_completed_30d = completed_result.scalar() or 0

    # Average quality score from quality assessments (last 30 days)
    quality_result = await db.execute(
        select(func.avg(QualityAssessment.overall_score)).where(
            QualityAssessment.stylist_id == staff_id,
            QualityAssessment.created_at >= thirty_days_ago,
        )
    )
    avg_quality_score = round(float(quality_result.scalar() or 0), 2)

    # Customer rating average from feedback
    rating_result = await db.execute(
        select(func.avg(CustomerFeedback.overall_rating)).where(
            CustomerFeedback.stylist_id == staff_id,
            CustomerFeedback.created_at >= thirty_days_ago,
        )
    )
    customer_rating_avg = round(float(rating_result.scalar() or 0), 2)

    # Rebooking rate: customers who rebooked within 60 days
    # Get unique customers served in the period
    unique_customers_result = await db.execute(
        select(func.count(func.distinct(Booking.customer_id))).where(
            Booking.stylist_id == staff_id,
            Booking.status == BookingStatus.COMPLETED,
            Booking.actual_end_at >= sixty_days_ago,
            Booking.actual_end_at < thirty_days_ago,
        )
    )
    unique_customers = unique_customers_result.scalar() or 0

    # Of those, how many rebooked
    if unique_customers > 0:
        rebooked_result = await db.execute(
            select(func.count(func.distinct(Booking.customer_id))).where(
                Booking.stylist_id == staff_id,
                Booking.status == BookingStatus.COMPLETED,
                Booking.actual_end_at >= thirty_days_ago,
                Booking.customer_id.in_(
                    select(Booking.customer_id).where(
                        Booking.stylist_id == staff_id,
                        Booking.status == BookingStatus.COMPLETED,
                        Booking.actual_end_at >= sixty_days_ago,
                        Booking.actual_end_at < thirty_days_ago,
                    )
                ),
            )
        )
        rebooked = rebooked_result.scalar() or 0
        rebooking_rate = round(rebooked / unique_customers * 100, 1)
    else:
        rebooking_rate = 0.0

    # Upsell rate: bookings with add_on_services / total bookings
    total_bookings_result = await db.execute(
        select(func.count(Booking.id)).where(
            Booking.stylist_id == staff_id,
            Booking.status == BookingStatus.COMPLETED,
            Booking.actual_end_at >= thirty_days_ago,
        )
    )
    total_bookings = total_bookings_result.scalar() or 0

    upsell_result = await db.execute(
        select(func.count(Booking.id)).where(
            Booking.stylist_id == staff_id,
            Booking.status == BookingStatus.COMPLETED,
            Booking.actual_end_at >= thirty_days_ago,
            Booking.add_on_services != None,
        )
    )
    upsell_bookings = upsell_result.scalar() or 0
    upsell_rate = round(upsell_bookings / max(total_bookings, 1) * 100, 1)

    # Average service time vs SOP expected time
    timing_result = await db.execute(
        select(func.avg(Booking.duration_variance_minutes)).where(
            Booking.stylist_id == staff_id,
            Booking.status == BookingStatus.COMPLETED,
            Booking.actual_end_at >= thirty_days_ago,
            Booking.duration_variance_minutes != None,
        )
    )
    avg_time_variance = round(float(timing_result.scalar() or 0), 1)

    # Complaint rate
    complaint_result = await db.execute(
        select(func.count(CustomerFeedback.id)).where(
            CustomerFeedback.stylist_id == staff_id,
            CustomerFeedback.created_at >= thirty_days_ago,
            CustomerFeedback.sentiment == Sentiment.NEGATIVE,
        )
    )
    complaints = complaint_result.scalar() or 0
    complaint_rate = round(complaints / max(services_completed_30d, 1) * 100, 1)

    # Revenue generated in last 30 days
    revenue_result = await db.execute(
        select(func.sum(Booking.final_price)).where(
            Booking.stylist_id == staff_id,
            Booking.status == BookingStatus.COMPLETED,
            Booking.actual_end_at >= thirty_days_ago,
        )
    )
    revenue_generated_30d = round(float(revenue_result.scalar() or 0), 2)

    # Top services
    top_services_result = await db.execute(
        select(Service.name, func.count(Booking.id).label("cnt"))
        .join(Booking, Booking.service_id == Service.id)
        .where(
            Booking.stylist_id == staff_id,
            Booking.status == BookingStatus.COMPLETED,
            Booking.actual_end_at >= thirty_days_ago,
        )
        .group_by(Service.name)
        .order_by(func.count(Booking.id).desc())
        .limit(5)
    )
    top_services = [{"service": row.name, "count": row.cnt} for row in top_services_result.all()]

    # Improvement areas from skill assessments
    gaps_result = await db.execute(
        select(SkillAssessment.skill_area, SkillAssessment.score).where(
            SkillAssessment.staff_id == staff_id,
        ).order_by(SkillAssessment.score.asc()).limit(3)
    )
    improvement_areas = [
        {"skill_area": row.skill_area, "score": float(row.score) if row.score else 0}
        for row in gaps_result.all()
    ]

    return APIResponse(
        success=True,
        data={
            "staff_id": staff_id,
            "services_completed_30d": services_completed_30d,
            "avg_quality_score": avg_quality_score,
            "customer_rating_avg": customer_rating_avg,
            "rebooking_rate": rebooking_rate,
            "upsell_rate": upsell_rate,
            "avg_service_time_vs_sop": f"{'+' if avg_time_variance > 0 else ''}{avg_time_variance} mins",
            "complaint_rate": complaint_rate,
            "revenue_generated_30d": revenue_generated_30d,
            "top_services": top_services,
            "improvement_areas": improvement_areas,
        },
    )


agent_stylist_360 = register_agent(AgentAction(
    name="stylist_performance_360",
    description="Multi-dimensional 360-degree stylist performance view with quality, revenue, and rebooking metrics",
    track="experience",
    feature="performance",
    method="get",
    path="/agents/track5/performance/360",
    handler=stylist_performance_360_handler,
    roles=["stylist", "salon_manager", "franchise_owner", "regional_manager"],
    ps_codes=["PS-05.08"],
))


# ═══════════════════════════════════════════════════════════════════════════════
# 52. ambient_intelligence (PS-05.09)
# ═══════════════════════════════════════════════════════════════════════════════

async def ambient_intelligence_handler(
    location_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "franchise_owner"])),
):
    """Context-aware environment recommendations based on occupancy and time of day."""
    now = datetime.now(timezone.utc)

    # Verify location
    loc_result = await db.execute(
        select(Location).where(Location.id == location_id)
    )
    location = loc_result.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    # Current occupancy: count active sessions at this location
    active_sessions_result = await db.execute(
        select(func.count(ServiceSession.id))
        .join(Booking, Booking.id == ServiceSession.booking_id)
        .where(
            Booking.location_id == location_id,
            ServiceSession.status == SessionStatus.ACTIVE,
        )
    )
    active_count = active_sessions_result.scalar() or 0

    # Waiting customers
    waiting_result = await db.execute(
        select(func.count(SmartQueueEntry.id)).where(
            SmartQueueEntry.location_id == location_id,
            SmartQueueEntry.status == QueueStatus.WAITING,
        )
    )
    waiting_count = waiting_result.scalar() or 0

    current_occupancy = active_count + waiting_count
    seating_capacity = location.seating_capacity or 20
    occupancy_pct = round(current_occupancy / max(seating_capacity, 1) * 100, 1)

    # Time of day phase
    local_hour = now.hour  # Simplified; in production, use location timezone
    if local_hour < 12:
        time_phase = "morning_calm"
    elif local_hour < 16:
        time_phase = "afternoon_rush"
    else:
        time_phase = "evening_wind_down"

    # Recommendations based on occupancy and time
    if occupancy_pct > 70:
        music_tempo = "upbeat"
        lighting = "bright"
    elif time_phase == "morning_calm":
        music_tempo = "slow"
        lighting = "warm"
    elif time_phase == "evening_wind_down":
        music_tempo = "slow"
        lighting = "warm"
    else:
        music_tempo = "medium"
        lighting = "neutral"

    # Promotional display content — services to promote based on low booking today
    thirty_days_ago = now - timedelta(days=30)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # High-margin services not booked much today
    today_booked_services = await db.execute(
        select(Booking.service_id).where(
            Booking.location_id == location_id,
            Booking.scheduled_at >= today_start,
            Booking.status != BookingStatus.CANCELLED,
        )
    )
    today_service_ids = {row[0] for row in today_booked_services.all()}

    promo_result = await db.execute(
        select(Service.name, Service.category, Service.base_price)
        .where(
            Service.is_active == True,
            ~Service.id.in_(today_service_ids) if today_service_ids else literal(True),
        )
        .order_by(Service.base_price.desc())
        .limit(3)
    )
    promotional_display = [
        {
            "service": row.name,
            "reason_to_promote": f"High-value {row.category} service not yet booked today",
        }
        for row in promo_result.all()
    ]

    # Customer mix insight
    today_bookings_result = await db.execute(
        select(Booking.source, func.count(Booking.id).label("cnt"))
        .where(
            Booking.location_id == location_id,
            Booking.scheduled_at >= today_start,
            Booking.status != BookingStatus.CANCELLED,
        )
        .group_by(Booking.source)
    )
    source_counts = {str(row.source): row.cnt for row in today_bookings_result.all()}
    walk_in_count = source_counts.get("BookingSource.WALK_IN", 0) + source_counts.get("walk_in", 0)
    app_count = source_counts.get("BookingSource.APP", 0) + source_counts.get("app", 0)
    total_today = sum(source_counts.values()) or 1

    # Determine mix from loyalty tiers
    premium_result = await db.execute(
        select(func.count(LoyaltyProgram.id)).where(
            LoyaltyProgram.tier.in_(["platinum", "gold"]),
            LoyaltyProgram.customer_id.in_(
                select(Booking.customer_id).where(
                    Booking.location_id == location_id,
                    Booking.scheduled_at >= today_start,
                    Booking.status != BookingStatus.CANCELLED,
                )
            ),
        )
    )
    premium_count = premium_result.scalar() or 0
    if premium_count / max(total_today, 1) > 0.5:
        customer_mix = "mostly_premium"
    elif walk_in_count / max(total_today, 1) > 0.5:
        customer_mix = "mostly_walk_in"
    else:
        customer_mix = "mixed"

    return APIResponse(
        success=True,
        data={
            "location_id": location_id,
            "location_name": location.name,
            "current_occupancy": current_occupancy,
            "seating_capacity": seating_capacity,
            "occupancy_pct": occupancy_pct,
            "time_of_day_phase": time_phase,
            "recommended_music_tempo": music_tempo,
            "recommended_lighting": lighting,
            "promotional_display_content": promotional_display,
            "customer_mix_insight": customer_mix,
            "active_services": active_count,
            "waiting_customers": waiting_count,
        },
    )


agent_ambient = register_agent(AgentAction(
    name="ambient_intelligence",
    description="Context-aware environment recommendations based on occupancy, time, and customer mix",
    track="experience",
    feature="ambient",
    method="get",
    path="/agents/track5/ambient/intelligence",
    handler=ambient_intelligence_handler,
    roles=["salon_manager", "franchise_owner"],
    ps_codes=["PS-05.09"],
))


# ═══════════════════════════════════════════════════════════════════════════════
# 53. checkout_cross_sell (PS-05.10)
# ═══════════════════════════════════════════════════════════════════════════════

class CheckoutCrossSellRequest(BaseModel):
    customer_id: str
    booking_id: str
    services_just_received: list[str]


async def checkout_cross_sell_handler(
    body: CheckoutCrossSellRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager"])),
):
    """Checkout cross-sell: product & service recommendations, loyalty points."""
    customer_id = body.customer_id
    booking_id = body.booking_id

    # Verify booking
    booking_result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = booking_result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Get services just received
    received_result = await db.execute(
        select(Service).where(Service.id.in_(body.services_just_received))
    )
    received_services = received_result.scalars().all()
    received_categories = {s.category for s in received_services if s.category}
    received_ids = {s.id for s in received_services}

    # Get customer profile
    cp_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.id == customer_id)
    )
    customer = cp_result.scalar_one_or_none()

    # Get customer's past services
    past_services_result = await db.execute(
        select(func.distinct(Booking.service_id)).where(
            Booking.customer_id == customer_id,
            Booking.status == BookingStatus.COMPLETED,
        )
    )
    past_service_ids = {row[0] for row in past_services_result.all()}

    # Product recommendations based on services received
    product_recs = []
    for svc in received_services:
        # Find home care products linked to this service's category
        product_result = await db.execute(
            select(InventoryItem).where(
                InventoryItem.location_id == booking.location_id,
                InventoryItem.category.ilike(f"%{svc.category}%") if svc.category else literal(False),
                InventoryItem.is_active == True,
                InventoryItem.current_stock > 0,
            ).limit(2)
        )
        for item in product_result.scalars().all():
            product_recs.append({
                "name": item.product_name,
                "reason": f"Recommended for maintaining your {svc.name} results at home",
                "price": float(item.cost_per_unit * 2) if item.cost_per_unit else None,
                "brand": item.brand,
            })

    # If no inventory matches, provide generic recommendations
    if not product_recs and received_services:
        for svc in received_services[:2]:
            product_recs.append({
                "name": f"{svc.category or svc.name} Home Care Kit",
                "reason": f"Keep your {svc.name} results lasting longer",
                "price": None,
                "brand": None,
            })

    # Service recommendations: complementary services not yet tried
    complement_map = {
        "haircut": ["hair color", "deep conditioning", "keratin"],
        "hair color": ["deep conditioning", "haircut", "gloss treatment"],
        "facial": ["skin treatment", "cleanup", "de-tan"],
        "spa": ["facial", "body massage", "manicure"],
        "manicure": ["pedicure", "nail art"],
        "pedicure": ["manicure", "foot spa"],
    }

    service_recs = []
    for cat in received_categories:
        complements = complement_map.get(cat.lower(), [])
        for comp_cat in complements:
            comp_svc_result = await db.execute(
                select(Service).where(
                    Service.category.ilike(f"%{comp_cat}%"),
                    Service.is_active == True,
                    ~Service.id.in_(received_ids),
                    ~Service.id.in_(past_service_ids) if past_service_ids else literal(True),
                ).limit(1)
            )
            comp_svc = comp_svc_result.scalar_one_or_none()
            if comp_svc:
                service_recs.append({
                    "name": comp_svc.name,
                    "reason": f"Complements your {cat} service perfectly",
                    "price": float(comp_svc.base_price),
                    "next_available_slot": None,
                })
        if len(service_recs) >= 3:
            break

    # Calculate loyalty points earned
    loyalty_result = await db.execute(
        select(LoyaltyProgram).where(LoyaltyProgram.customer_id == customer_id)
    )
    loyalty = loyalty_result.scalar_one_or_none()

    final_price = float(booking.final_price or booking.base_price or 0)
    points_earned = int(final_price / 10)  # 1 point per 10 currency units

    if loyalty:
        # Record transaction
        lt = LoyaltyTransaction(
            id=generate_uuid(),
            loyalty_program_id=loyalty.id,
            booking_id=booking_id,
            transaction_type="earn",
            points=points_earned,
            description=f"Points earned from booking {booking.booking_number}",
        )
        db.add(lt)
        loyalty.total_points = (loyalty.total_points or 0) + points_earned
        loyalty.redeemable_points = (loyalty.redeemable_points or 0) + points_earned
        loyalty.lifetime_points_earned = (loyalty.lifetime_points_earned or 0) + points_earned

    # Personalized message
    cust_user_result = await db.execute(
        select(User).where(User.id == customer.user_id) if customer else select(User).where(literal(False))
    )
    cust_user = cust_user_result.scalar_one_or_none()
    customer_name = cust_user.first_name if cust_user else "there"
    svc_names = ", ".join(s.name for s in received_services[:3])

    personalized_message = (
        f"Thank you, {customer_name}! Your {svc_names} turned out beautifully. "
        f"You earned {points_earned} loyalty points today!"
    )

    # Save recommendations for tracking
    for rec in service_recs:
        sr = ServiceRecommendation(
            id=generate_uuid(),
            booking_id=booking_id,
            customer_id=customer_id,
            location_id=booking.location_id,
            recommendation_type="cross_sell",
            trigger_context="checkout",
            reason=rec["reason"],
        )
        db.add(sr)

    return APIResponse(
        success=True,
        data={
            "customer_id": customer_id,
            "booking_id": booking_id,
            "product_recommendations": product_recs[:5],
            "service_recommendations": service_recs[:3],
            "loyalty_points_earned": points_earned,
            "total_loyalty_points": loyalty.total_points if loyalty else points_earned,
            "personalized_message": personalized_message,
        },
    )


agent_checkout_cross_sell = register_agent(AgentAction(
    name="checkout_cross_sell",
    description="Checkout cross-sell engine with product and service recommendations plus loyalty points",
    track="experience",
    feature="checkout",
    method="post",
    path="/agents/track5/checkout/cross-sell",
    handler=checkout_cross_sell_handler,
    roles=["stylist", "salon_manager"],
    ps_codes=["PS-05.10"],
))
