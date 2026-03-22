"""Track 2: Staff Intelligence & Development agents.

Covers PS-02.01 through PS-02.10 — client transition planning, AI upsell,
onboarding tracking, smart scheduling, attrition risk, knowledge management,
consultation coaching, skill competency, capacity rebalancing, product guidance.
"""
from datetime import datetime, timezone, timedelta, date

from fastapi import Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func, case, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, enum_val
from app.dependencies import get_current_user, require_role
from app.schemas.common import APIResponse
from app.agents import AgentAction, register_agent
from app.models.user import User
from app.models.customer import CustomerProfile
from app.models.service import Service, SOP
from app.models.booking import Booking, BookingStatus
from app.models.session import ServiceSession, SessionStatus
from app.models.quality import QualityAssessment, SkillAssessment
from app.models.staff import StaffProfile, SkillLevel
from app.models.feedback import CustomerFeedback
from app.models.training import TrainingRecord
from app.models.location import Location
from app.models.knowledge import KnowledgeBaseEntry
from app.models.scheduling import StaffSchedule
from app.models.recommendation import ServiceRecommendation


# ─────────────────────────────────────────────────────────────
# 13. CLIENT TRANSITION PLAN  (PS-02.01)
# ─────────────────────────────────────────────────────────────

class ClientTransitionRequest(BaseModel):
    departing_stylist_id: str
    location_id: str


async def client_transition_plan_handler(
    body: ClientTransitionRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "regional_manager", "super_admin"])),
):
    """Generate a transition plan for clients of a departing stylist."""

    # Verify the departing stylist exists
    dep_result = await db.execute(
        select(StaffProfile).where(StaffProfile.id == body.departing_stylist_id)
    )
    departing_stylist = dep_result.scalar_one_or_none()
    if not departing_stylist:
        raise HTTPException(status_code=404, detail="Departing stylist not found")

    # Find all customers who have this stylist as preferred
    customers_q = await db.execute(
        select(CustomerProfile)
        .where(CustomerProfile.preferred_stylist_id == body.departing_stylist_id)
    )
    affected_customers = customers_q.scalars().all()

    if not affected_customers:
        return APIResponse(
            success=True,
            data={
                "departing_stylist_id": body.departing_stylist_id,
                "transition_plan": [],
                "affected_customers_count": 0,
                "message": "No customers have this stylist as their preferred stylist",
            },
        )

    # Fetch all available replacement stylists at the same location
    replacements_q = await db.execute(
        select(StaffProfile)
        .where(
            StaffProfile.location_id == body.location_id,
            StaffProfile.id != body.departing_stylist_id,
            StaffProfile.is_available == True,
        )
    )
    available_replacements = replacements_q.scalars().all()

    if not available_replacements:
        return APIResponse(
            success=True,
            data={
                "departing_stylist_id": body.departing_stylist_id,
                "transition_plan": [],
                "affected_customers_count": len(affected_customers),
                "message": "No available replacement stylists at this location",
            },
        )

    departing_specializations = set(departing_stylist.specializations or [])
    skill_levels_map = {"L1": 1, "L2": 2, "L3": 3}
    departing_level = skill_levels_map.get(
        enum_val(departing_stylist.skill_level) if departing_stylist.skill_level else "L1", 1
    )

    transition_plan = []
    for customer in affected_customers:
        # Score each replacement candidate
        candidates = []
        for rep in available_replacements:
            rep_specializations = set(rep.specializations or [])
            rep_level = skill_levels_map.get(
                enum_val(rep.skill_level) if rep.skill_level else "L1", 1
            )

            # Matching score components
            spec_overlap = len(departing_specializations & rep_specializations)
            spec_total = max(len(departing_specializations), 1)
            spec_score = (spec_overlap / spec_total) * 40  # up to 40 pts

            skill_score = 30 if rep_level >= departing_level else max(0, 30 - (departing_level - rep_level) * 15)

            rating_score = min(30, (float(rep.current_rating or 3) / 5.0) * 30)

            total_score = round(spec_score + skill_score + rating_score, 1)

            reasons = []
            if spec_overlap > 0:
                reasons.append(f"Matching specializations: {', '.join(departing_specializations & rep_specializations)}")
            if rep_level >= departing_level:
                reasons.append(f"Skill level {enum_val(rep.skill_level) if rep.skill_level else 'L1'} meets or exceeds requirement")
            if float(rep.current_rating or 0) >= 4.0:
                reasons.append(f"High rating ({float(rep.current_rating or 0):.1f})")

            candidates.append({
                "stylist_id": rep.id,
                "employee_id": rep.employee_id,
                "match_score": total_score,
                "skill_level": enum_val(rep.skill_level) if rep.skill_level else "L1",
                "specializations": rep.specializations or [],
                "current_rating": float(rep.current_rating or 0),
                "reason": "; ".join(reasons) if reasons else "Available at same location",
            })

        # Sort by match score and pick the best
        candidates.sort(key=lambda x: x["match_score"], reverse=True)
        best_match = candidates[0] if candidates else None

        transition_plan.append({
            "customer_id": customer.id,
            "customer_total_visits": customer.total_visits,
            "customer_lifetime_value": float(customer.lifetime_value or 0),
            "recommended_stylist": best_match,
            "alternate_stylists": candidates[1:3] if len(candidates) > 1 else [],
        })

    # Sort plan by customer lifetime value (highest first)
    transition_plan.sort(key=lambda x: x["customer_lifetime_value"], reverse=True)

    return APIResponse(
        success=True,
        data={
            "departing_stylist_id": body.departing_stylist_id,
            "location_id": body.location_id,
            "affected_customers_count": len(affected_customers),
            "replacement_candidates_count": len(available_replacements),
            "transition_plan": transition_plan,
        },
    )


register_agent(AgentAction(
    name="client_transition_plan",
    description="Generate client transition plan when a stylist departs, matching replacements by skill and specialization",
    track="staff",
    feature="transition",
    method="post",
    path="/agents/track2/staff/transition-plan",
    handler=client_transition_plan_handler,
    roles=["salon_manager", "regional_manager", "super_admin"],
    ps_codes=["PS-02.01"],
    requires_ai=False,
))


# ─────────────────────────────────────────────────────────────
# 14. AI UPSELL SUGGESTIONS  (PS-02.02)
# ─────────────────────────────────────────────────────────────

class AIUpsellRequest(BaseModel):
    customer_id: str
    current_service_id: str
    booking_id: str


async def ai_upsell_suggestions_handler(
    body: AIUpsellRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager"])),
):
    """Analyze customer profile and history to generate upsell recommendations."""

    # Fetch customer
    cp_result = await db.execute(select(CustomerProfile).where(CustomerProfile.id == body.customer_id))
    customer = cp_result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Fetch current service
    svc_result = await db.execute(select(Service).where(Service.id == body.current_service_id))
    current_service = svc_result.scalar_one_or_none()
    if not current_service:
        raise HTTPException(status_code=404, detail="Service not found")

    current_category = (current_service.category or "").lower()

    # Fetch customer's recent services (to avoid recommending the same thing)
    recent_q = await db.execute(
        select(Booking.service_id)
        .where(
            Booking.customer_id == body.customer_id,
            Booking.status == BookingStatus.COMPLETED,
        )
        .order_by(Booking.scheduled_at.desc())
        .limit(10)
    )
    recent_service_ids = {row.service_id for row in recent_q.all()}

    # Fetch available add-on / complementary services
    all_services_q = await db.execute(
        select(Service)
        .where(
            Service.is_active == True,
            Service.id != body.current_service_id,
        )
    )
    all_services = all_services_q.scalars().all()

    recommendations = []

    for svc in all_services:
        confidence = 0.0
        reasons = []
        suggested_script = ""

        svc_category = (svc.category or "").lower()

        # Hair damage -> recommend treatment
        if customer.hair_damage_level and customer.hair_damage_level >= 5:
            if "treatment" in svc_category or "repair" in svc_category:
                confidence += 0.35
                reasons.append(f"Hair damage level is {customer.hair_damage_level}/10")
                suggested_script = "I noticed your hair could benefit from a deep conditioning treatment. Would you like to add one today?"

        # Skin concerns -> recommend skin services
        if customer.primary_skin_concerns and svc_category in ("skin", "facial", "skincare"):
            concerns_str = ", ".join(customer.primary_skin_concerns[:3])
            confidence += 0.30
            reasons.append(f"Customer has skin concerns: {concerns_str}")
            suggested_script = f"Based on your skin profile, a {svc.name} could help with {concerns_str}."

        # Complementary category pairing
        category_pairs = {
            "hair": ["hair treatment", "scalp treatment", "hair spa"],
            "hair colour": ["hair treatment", "hair gloss"],
            "facial": ["skin care", "cleanup"],
            "haircut": ["hair spa", "hair treatment", "blow dry"],
            "bridal": ["facial", "makeup", "nail art"],
        }
        complementary = category_pairs.get(current_category, [])
        if svc_category in complementary:
            confidence += 0.25
            reasons.append(f"Complementary to {current_service.name}")
            if not suggested_script:
                suggested_script = f"Many clients pair {current_service.name} with a {svc.name}. Would you like to try it?"

        # Not recently done -> slight boost
        if svc.id not in recent_service_ids and confidence > 0:
            confidence += 0.10
            reasons.append("Customer hasn't had this service recently")

        # Price-appropriate (don't upsell something more expensive than 2x current)
        if svc.base_price and current_service.base_price:
            if float(svc.base_price) > float(current_service.base_price) * 2:
                confidence *= 0.5  # Reduce confidence for very expensive upsells

        if confidence >= 0.20:
            recommendations.append({
                "service_id": svc.id,
                "service_name": svc.name,
                "category": svc.category,
                "reason": "; ".join(reasons),
                "confidence": round(min(confidence, 1.0), 2),
                "suggested_script": suggested_script,
                "estimated_revenue": float(svc.base_price or 0),
                "duration_minutes": svc.duration_minutes,
            })

    # Sort by confidence, take top 3
    recommendations.sort(key=lambda x: x["confidence"], reverse=True)
    recommendations = recommendations[:3]

    # Record recommendations
    for rec in recommendations:
        db_rec = ServiceRecommendation(
            booking_id=body.booking_id,
            customer_id=body.customer_id,
            recommendation_type="upsell",
            trigger_context="in_service",
            recommended_service_id=rec["service_id"],
            reason=rec["reason"],
            confidence_score=rec["confidence"],
        )
        db.add(db_rec)
    await db.flush()

    return APIResponse(
        success=True,
        data={
            "customer_id": body.customer_id,
            "current_service": current_service.name,
            "recommendations": recommendations,
            "total_potential_revenue": sum(r["estimated_revenue"] for r in recommendations),
        },
    )


register_agent(AgentAction(
    name="ai_upsell_suggestions",
    description="Generate upsell recommendations based on customer profile, hair/skin analysis, and service history",
    track="staff",
    feature="upsell",
    method="post",
    path="/agents/track2/staff/upsell",
    handler=ai_upsell_suggestions_handler,
    roles=["stylist", "salon_manager"],
    ps_codes=["PS-02.02"],
    requires_ai=False,
))


# ─────────────────────────────────────────────────────────────
# 15. ONBOARDING PROGRESS  (PS-02.03)
# ─────────────────────────────────────────────────────────────

async def onboarding_progress_handler(
    staff_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "regional_manager", "super_admin"])),
):
    """Return onboarding progress for a staff member including trainings and readiness."""

    # Fetch staff profile
    staff_result = await db.execute(select(StaffProfile).where(StaffProfile.id == staff_id))
    staff = staff_result.scalar_one_or_none()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff profile not found")

    # Calculate days since joining
    days_since_join = None
    if staff.joining_date:
        join_date = staff.joining_date if isinstance(staff.joining_date, date) else date.fromisoformat(str(staff.joining_date))
        days_since_join = (date.today() - join_date).days

    # Fetch all training records
    trainings_q = await db.execute(
        select(TrainingRecord)
        .where(TrainingRecord.staff_id == staff_id)
        .order_by(TrainingRecord.start_date.desc())
    )
    trainings = trainings_q.scalars().all()

    completed_trainings = [t for t in trainings if t.passed]
    pending_trainings = [t for t in trainings if not t.passed]

    training_summary = {
        "completed": [
            {
                "id": t.id,
                "name": t.training_name,
                "type": enum_val(t.training_type) if t.training_type else None,
                "category": t.service_category,
                "score": float(t.score) if t.score else None,
                "hours": float(t.hours_completed) if t.hours_completed else 0,
                "end_date": str(t.end_date) if t.end_date else None,
                "includes_soulskin": t.includes_soulskin,
            }
            for t in completed_trainings
        ],
        "pending": [
            {
                "id": t.id,
                "name": t.training_name,
                "type": enum_val(t.training_type) if t.training_type else None,
                "category": t.service_category,
                "start_date": str(t.start_date) if t.start_date else None,
                "hours_completed": float(t.hours_completed) if t.hours_completed else 0,
            }
            for t in pending_trainings
        ],
    }

    # Services they can independently handle (based on skill level)
    skill_levels_map = {"L1": 1, "L2": 2, "L3": 3}
    staff_level_num = skill_levels_map.get(enum_val(staff.skill_level) if staff.skill_level else "L1", 1)

    can_do_q = await db.execute(
        select(Service.id, Service.name, Service.category, Service.skill_required)
        .where(Service.is_active == True)
    )
    can_do_services = []
    cannot_do_services = []
    for svc in can_do_q.all():
        req_level = skill_levels_map.get(enum_val(svc.skill_required) if svc.skill_required else "L1", 1)
        entry = {"service_id": svc.id, "name": svc.name, "category": svc.category, "required_level": enum_val(svc.skill_required) if svc.skill_required else "L1"}
        if staff_level_num >= req_level:
            can_do_services.append(entry)
        else:
            cannot_do_services.append(entry)

    # Mentor sessions (on_job training records)
    mentor_sessions_q = await db.execute(
        select(func.count(TrainingRecord.id))
        .where(
            TrainingRecord.staff_id == staff_id,
            TrainingRecord.training_type == "on_job",
        )
    )
    mentor_sessions = mentor_sessions_q.scalar() or 0

    # Required trainings checklist (standard set)
    required_categories = ["hair", "skin", "chemical_safety", "customer_service", "soulskin"]
    completed_categories = {t.service_category for t in completed_trainings if t.service_category}
    missing_categories = [c for c in required_categories if c not in completed_categories]

    # Readiness percentage
    total_required = len(required_categories) + 3  # +3 for mentor sessions, days threshold, skill
    achieved = len(completed_categories & set(required_categories))
    if mentor_sessions >= 5:
        achieved += 1
    if days_since_join and days_since_join >= 30:
        achieved += 1
    if staff_level_num >= 2:
        achieved += 1
    readiness_pct = round((achieved / total_required) * 100, 1) if total_required > 0 else 0

    # Projected readiness date
    projected_readiness_date = None
    if readiness_pct < 100 and days_since_join is not None:
        # Estimate based on current progress rate
        if readiness_pct > 0 and days_since_join > 0:
            full_days = int(days_since_join * (100 / readiness_pct))
            remaining_days = full_days - days_since_join
            projected_readiness_date = str(date.today() + timedelta(days=remaining_days))
        else:
            projected_readiness_date = str(date.today() + timedelta(days=90))  # default 90 days

    return APIResponse(
        success=True,
        data={
            "staff_id": staff_id,
            "employee_id": staff.employee_id,
            "designation": staff.designation,
            "skill_level": enum_val(staff.skill_level) if staff.skill_level else "L1",
            "joining_date": str(staff.joining_date) if staff.joining_date else None,
            "days_since_join": days_since_join,
            "readiness_pct": readiness_pct,
            "projected_readiness_date": projected_readiness_date,
            "trainings": training_summary,
            "total_trainings_completed": len(completed_trainings),
            "total_trainings_pending": len(pending_trainings),
            "mentor_sessions_logged": mentor_sessions,
            "services_can_handle": can_do_services,
            "services_cannot_handle": cannot_do_services,
            "missing_required_categories": missing_categories,
            "soulskin_certified": staff.soulskin_certified,
            "total_hours_trained": sum(float(t.hours_completed or 0) for t in trainings),
        },
    )


register_agent(AgentAction(
    name="onboarding_progress",
    description="Track onboarding progress: trainings, skill readiness, mentor sessions, service capabilities",
    track="staff",
    feature="onboarding",
    method="get",
    path="/agents/track2/staff/onboarding",
    handler=onboarding_progress_handler,
    roles=["salon_manager", "regional_manager", "super_admin"],
    ps_codes=["PS-02.03"],
    requires_ai=False,
))


# ─────────────────────────────────────────────────────────────
# 16. SMART SCHEDULING  (PS-02.04)
# ─────────────────────────────────────────────────────────────

class SmartSchedulingRequest(BaseModel):
    location_id: str
    date: str  # ISO format YYYY-MM-DD


async def smart_scheduling_handler(
    body: SmartSchedulingRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "regional_manager", "super_admin"])),
):
    """Generate optimized booking-to-stylist assignments based on skill matching."""

    target_date = date.fromisoformat(body.date)

    # Get all bookings for that day at this location
    day_start = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0, tzinfo=timezone.utc)
    day_end = day_start + timedelta(days=1)

    bookings_q = await db.execute(
        select(Booking, Service)
        .join(Service, Booking.service_id == Service.id)
        .where(
            Booking.location_id == body.location_id,
            Booking.scheduled_at >= day_start,
            Booking.scheduled_at < day_end,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
        )
        .order_by(Booking.scheduled_at)
    )
    bookings_with_services = bookings_q.all()

    if not bookings_with_services:
        return APIResponse(
            success=True,
            data={
                "location_id": body.location_id,
                "date": body.date,
                "optimized_schedule": [],
                "message": "No bookings found for this date",
            },
        )

    # Get available staff for the day
    # First check StaffSchedule, fallback to StaffProfile availability
    schedule_q = await db.execute(
        select(StaffSchedule)
        .where(
            StaffSchedule.location_id == body.location_id,
            StaffSchedule.date == target_date,
            StaffSchedule.is_available == True,
        )
    )
    scheduled_staff_ids = {s.staff_id for s in schedule_q.scalars().all()}

    # Also get staff from profiles if no schedule entries exist
    staff_q = await db.execute(
        select(StaffProfile)
        .where(
            StaffProfile.location_id == body.location_id,
            StaffProfile.is_available == True,
        )
    )
    all_staff = staff_q.scalars().all()

    # Use scheduled staff if schedule entries exist, otherwise all available staff
    available_staff = [s for s in all_staff if (not scheduled_staff_ids or s.id in scheduled_staff_ids)]

    if not available_staff:
        return APIResponse(
            success=True,
            data={
                "location_id": body.location_id,
                "date": body.date,
                "optimized_schedule": [],
                "message": "No available staff for this date",
            },
        )

    skill_levels_map = {"L1": 1, "L2": 2, "L3": 3}

    optimized_schedule = []
    mismatches = []
    staff_load = {s.id: 0 for s in available_staff}  # Track assignments per stylist

    for booking, service in bookings_with_services:
        required_level_value = enum_val(service.skill_required) if service.skill_required else "L1"
        required_level_num = skill_levels_map.get(required_level_value, 1)

        # Score each available staff for this booking
        candidates = []
        for staff in available_staff:
            staff_level_num = skill_levels_map.get(enum_val(staff.skill_level) if staff.skill_level else "L1", 1)

            # Skill level match score
            if staff_level_num >= required_level_num:
                skill_match = 40
            else:
                skill_match = max(0, 40 - (required_level_num - staff_level_num) * 20)

            # Specialization match
            staff_specs = set(staff.specializations or [])
            service_category = (service.category or "").lower()
            spec_match = 20 if service_category in {s.lower() for s in staff_specs} else 0

            # Load balancing (prefer less-loaded staff)
            load_penalty = min(20, staff_load.get(staff.id, 0) * 5)
            load_score = 20 - load_penalty

            # Rating bonus
            rating_score = min(20, (float(staff.current_rating or 3) / 5.0) * 20)

            total_score = skill_match + spec_match + load_score + rating_score

            # Chemical services require L2+
            is_valid = True
            match_reason = []
            if service.is_chemical and staff_level_num < 2:
                is_valid = False
                match_reason.append("Chemical service requires L2+")
            elif required_level_num > staff_level_num:
                is_valid = False
                match_reason.append(f"Service requires {required_level_value}, staff is {enum_val(staff.skill_level) if staff.skill_level else 'L1'}")

            if staff_level_num >= required_level_num:
                match_reason.append(f"Skill level {enum_val(staff.skill_level) if staff.skill_level else 'L1'} matches requirement")
            if spec_match > 0:
                match_reason.append(f"Specialization in {service_category}")

            candidates.append({
                "staff_id": staff.id,
                "employee_id": staff.employee_id,
                "skill_level": enum_val(staff.skill_level) if staff.skill_level else "L1",
                "skill_match_score": round(total_score, 1),
                "is_valid": is_valid,
                "match_reason": "; ".join(match_reason),
            })

        # Sort by validity first, then score
        candidates.sort(key=lambda x: (x["is_valid"], x["skill_match_score"]), reverse=True)
        best = candidates[0] if candidates else None

        if best:
            staff_load[best["staff_id"]] = staff_load.get(best["staff_id"], 0) + 1

        is_mismatch = best and not best["is_valid"]
        if is_mismatch:
            mismatches.append(booking.id)

        optimized_schedule.append({
            "booking_id": booking.id,
            "booking_number": booking.booking_number,
            "scheduled_at": str(booking.scheduled_at),
            "service_name": service.name,
            "service_category": service.category,
            "is_chemical": service.is_chemical,
            "skill_required": required_level_value,
            "current_stylist_id": booking.stylist_id,
            "recommended_stylist": best,
            "is_mismatch": is_mismatch,
        })

    return APIResponse(
        success=True,
        data={
            "location_id": body.location_id,
            "date": body.date,
            "total_bookings": len(bookings_with_services),
            "available_staff": len(available_staff),
            "mismatch_count": len(mismatches),
            "optimized_schedule": optimized_schedule,
            "staff_workload": [
                {"staff_id": sid, "assigned_bookings": count}
                for sid, count in staff_load.items()
            ],
        },
    )


register_agent(AgentAction(
    name="smart_scheduling",
    description="Optimize booking-to-stylist assignments by skill matching, specialization, and load balancing",
    track="staff",
    feature="scheduling",
    method="post",
    path="/agents/track2/staff/smart-schedule",
    handler=smart_scheduling_handler,
    roles=["salon_manager", "regional_manager", "super_admin"],
    ps_codes=["PS-02.04"],
    requires_ai=False,
))


# ─────────────────────────────────────────────────────────────
# 17. ATTRITION RISK SCAN  (PS-02.05)
# ─────────────────────────────────────────────────────────────

async def attrition_risk_scan_handler(
    location_id: str = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "regional_manager", "super_admin"])),
):
    """Scan staff for attrition risk based on performance trends and engagement signals."""

    staff_filter = []
    if location_id:
        staff_filter.append(StaffProfile.location_id == location_id)

    staff_q = await db.execute(
        select(StaffProfile, User.first_name, User.last_name)
        .join(User, StaffProfile.user_id == User.id)
        .where(*staff_filter)
    )
    staff_rows = staff_q.all()

    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    sixty_days_ago = datetime.now(timezone.utc) - timedelta(days=60)

    risk_results = []

    for staff, first_name, last_name in staff_rows:
        signals = []
        risk_score = 0.0

        # 1. Services done trend (compare last 30 days vs previous 30 days)
        recent_services_q = await db.execute(
            select(func.count(Booking.id))
            .where(
                Booking.stylist_id == staff.id,
                Booking.status == BookingStatus.COMPLETED,
                Booking.actual_end_at >= thirty_days_ago,
            )
        )
        recent_count = recent_services_q.scalar() or 0

        prev_services_q = await db.execute(
            select(func.count(Booking.id))
            .where(
                Booking.stylist_id == staff.id,
                Booking.status == BookingStatus.COMPLETED,
                Booking.actual_end_at >= sixty_days_ago,
                Booking.actual_end_at < thirty_days_ago,
            )
        )
        prev_count = prev_services_q.scalar() or 0

        if prev_count > 0 and recent_count < prev_count * 0.7:
            risk_score += 0.25
            signals.append(f"Service volume declining: {recent_count} (last 30d) vs {prev_count} (prev 30d)")

        # 2. Rating trend
        recent_rating_q = await db.execute(
            select(func.avg(CustomerFeedback.stylist_rating))
            .where(
                CustomerFeedback.stylist_id == staff.id,
                CustomerFeedback.created_at >= thirty_days_ago,
            )
        )
        recent_rating = recent_rating_q.scalar()

        prev_rating_q = await db.execute(
            select(func.avg(CustomerFeedback.stylist_rating))
            .where(
                CustomerFeedback.stylist_id == staff.id,
                CustomerFeedback.created_at >= sixty_days_ago,
                CustomerFeedback.created_at < thirty_days_ago,
            )
        )
        prev_rating = prev_rating_q.scalar()

        if prev_rating and recent_rating and float(recent_rating) < float(prev_rating) * 0.85:
            risk_score += 0.20
            signals.append(f"Rating dropping: {float(recent_rating):.1f} (recent) vs {float(prev_rating):.1f} (prev)")

        # 3. Days since last training
        last_training_q = await db.execute(
            select(func.max(TrainingRecord.end_date))
            .where(TrainingRecord.staff_id == staff.id, TrainingRecord.passed == True)
        )
        last_training_date = last_training_q.scalar()
        days_since_training = None
        if last_training_date:
            ltd = last_training_date if isinstance(last_training_date, date) else date.fromisoformat(str(last_training_date))
            days_since_training = (date.today() - ltd).days
            if days_since_training > 90:
                risk_score += 0.15
                signals.append(f"No training in {days_since_training} days")
        else:
            risk_score += 0.10
            signals.append("No training records found")

        # 4. Recent complaints
        complaint_q = await db.execute(
            select(func.count(CustomerFeedback.id))
            .where(
                CustomerFeedback.stylist_id == staff.id,
                CustomerFeedback.created_at >= thirty_days_ago,
                CustomerFeedback.overall_rating <= 2,
            )
        )
        complaint_count = complaint_q.scalar() or 0
        if complaint_count >= 3:
            risk_score += 0.25
            signals.append(f"{complaint_count} complaints in the last 30 days")
        elif complaint_count >= 1:
            risk_score += 0.10
            signals.append(f"{complaint_count} complaint(s) in the last 30 days")

        # 5. Use stored attrition risk score as a supplementary signal
        if staff.attrition_risk_score:
            stored_risk = float(staff.attrition_risk_score)
            risk_score = (risk_score + stored_risk) / 2  # Average with stored

        risk_score = round(min(risk_score, 1.0), 2)

        # Determine label
        if risk_score >= 0.7:
            risk_label = "high"
            recommended_intervention = "Immediate one-on-one meeting. Review compensation and career path."
        elif risk_score >= 0.4:
            risk_label = "medium"
            recommended_intervention = "Schedule check-in. Offer training opportunities and recognition."
        else:
            risk_label = "low"
            recommended_intervention = "Continue regular engagement. Monitor trends."

        risk_results.append({
            "staff_id": staff.id,
            "employee_id": staff.employee_id,
            "name": f"{first_name} {last_name}",
            "skill_level": enum_val(staff.skill_level) if staff.skill_level else "L1",
            "risk_score": risk_score,
            "risk_label": risk_label,
            "signals": signals,
            "recommended_intervention": recommended_intervention,
            "days_since_last_training": days_since_training,
            "recent_complaint_count": complaint_count,
            "recent_services_count": recent_count,
        })

    # Sort by risk score descending
    risk_results.sort(key=lambda x: x["risk_score"], reverse=True)

    high_risk_count = sum(1 for r in risk_results if r["risk_label"] == "high")
    medium_risk_count = sum(1 for r in risk_results if r["risk_label"] == "medium")

    return APIResponse(
        success=True,
        data={
            "location_id": location_id,
            "total_staff_scanned": len(risk_results),
            "high_risk_count": high_risk_count,
            "medium_risk_count": medium_risk_count,
            "risk_results": risk_results,
        },
    )


register_agent(AgentAction(
    name="attrition_risk_scan",
    description="Scan staff for attrition risk using performance trends, complaint frequency, and training recency",
    track="staff",
    feature="retention",
    method="get",
    path="/agents/track2/staff/attrition-risk",
    handler=attrition_risk_scan_handler,
    roles=["salon_manager", "regional_manager", "super_admin"],
    ps_codes=["PS-02.05"],
    requires_ai=False,
))


# ─────────────────────────────────────────────────────────────
# 18. KNOWLEDGE CAPTURE  (PS-02.06)
# ─────────────────────────────────────────────────────────────

class KnowledgeCaptureRequest(BaseModel):
    staff_id: str
    knowledge_type: str  # product_tip, service_combo, customer_insight
    content: str
    service_category: str | None = None
    title: str | None = None


async def knowledge_capture_handler(
    body: KnowledgeCaptureRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager"])),
):
    """Store a knowledge base entry contributed by staff."""

    # Validate knowledge_type
    valid_types = ["product_tip", "service_combo", "customer_insight"]
    if body.knowledge_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid knowledge_type. Must be one of: {', '.join(valid_types)}",
        )

    # Verify staff exists
    staff_result = await db.execute(select(StaffProfile).where(StaffProfile.id == body.staff_id))
    staff = staff_result.scalar_one_or_none()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff profile not found")

    # Auto-generate title if not provided
    title = body.title or f"{body.knowledge_type.replace('_', ' ').title()} by {staff.employee_id}"

    # Generate tags from content keywords
    stop_words = {"the", "a", "an", "is", "it", "to", "and", "of", "in", "for", "on", "with", "at", "by", "from"}
    words = body.content.lower().split()
    tags = list({w.strip(".,!?;:") for w in words if len(w) > 3 and w not in stop_words})[:10]

    entry = KnowledgeBaseEntry(
        staff_id=body.staff_id,
        knowledge_type=body.knowledge_type,
        service_category=body.service_category,
        title=title,
        content=body.content,
        tags=tags,
    )
    db.add(entry)
    await db.flush()

    return APIResponse(
        success=True,
        data={
            "id": entry.id,
            "staff_id": body.staff_id,
            "knowledge_type": body.knowledge_type,
            "title": title,
            "service_category": body.service_category,
            "tags": tags,
        },
        message="Knowledge entry captured successfully",
    )


register_agent(AgentAction(
    name="knowledge_capture",
    description="Capture staff-contributed knowledge: product tips, service combos, customer insights",
    track="staff",
    feature="knowledge",
    method="post",
    path="/agents/track2/staff/knowledge/capture",
    handler=knowledge_capture_handler,
    roles=["stylist", "salon_manager"],
    ps_codes=["PS-02.06"],
    requires_ai=False,
))


# ─────────────────────────────────────────────────────────────
# 19. KNOWLEDGE SEARCH  (PS-02.06)
# ─────────────────────────────────────────────────────────────

async def knowledge_search_handler(
    query: str = Query(...),
    service_category: str = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager"])),
):
    """Search the knowledge base for matching tips and insights."""

    filters = []
    if service_category:
        filters.append(KnowledgeBaseEntry.service_category == service_category)

    # Fetch all entries (with optional category filter)
    entries_q = await db.execute(
        select(KnowledgeBaseEntry)
        .where(*filters)
        .order_by(KnowledgeBaseEntry.created_at.desc())
    )
    all_entries = entries_q.scalars().all()

    # Simple keyword matching (in a production system you'd use full-text search or vector similarity)
    query_terms = {w.lower().strip(".,!?;:") for w in query.split() if len(w) > 2}

    scored_entries = []
    for entry in all_entries:
        score = 0.0
        content_lower = (entry.content or "").lower()
        title_lower = (entry.title or "").lower()
        entry_tags = set(entry.tags or [])

        for term in query_terms:
            if term in title_lower:
                score += 3.0
            if term in content_lower:
                score += 1.0
            if term in entry_tags:
                score += 2.0

        if score > 0:
            scored_entries.append({
                "id": entry.id,
                "title": entry.title,
                "content": entry.content,
                "knowledge_type": entry.knowledge_type,
                "service_category": entry.service_category,
                "staff_id": entry.staff_id,
                "tags": entry.tags,
                "upvotes": entry.upvotes,
                "is_verified": entry.is_verified,
                "relevance_score": round(score, 1),
                "created_at": str(entry.created_at),
            })

    # Sort by relevance
    scored_entries.sort(key=lambda x: x["relevance_score"], reverse=True)

    return APIResponse(
        success=True,
        data={
            "query": query,
            "service_category": service_category,
            "results_count": len(scored_entries),
            "results": scored_entries[:20],  # Limit to 20 results
        },
    )


register_agent(AgentAction(
    name="knowledge_search",
    description="Search the staff knowledge base for tips, combos, and insights by keyword",
    track="staff",
    feature="knowledge",
    method="get",
    path="/agents/track2/staff/knowledge/search",
    handler=knowledge_search_handler,
    roles=["stylist", "salon_manager"],
    ps_codes=["PS-02.06"],
    requires_ai=False,
))


# ─────────────────────────────────────────────────────────────
# 20. AI CONSULTATION COACH  (PS-02.07)
# ─────────────────────────────────────────────────────────────

class ConsultationCoachRequest(BaseModel):
    customer_id: str
    service_category: str


async def ai_consultation_coach_handler(
    body: ConsultationCoachRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager"])),
):
    """Generate a consultation coaching script based on customer profile and service category."""

    # Fetch customer
    cp_result = await db.execute(select(CustomerProfile).where(CustomerProfile.id == body.customer_id))
    customer = cp_result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Fetch user details for greeting
    user_q = await db.execute(select(User).where(User.id == customer.user_id))
    cust_user = user_q.scalar_one_or_none()
    customer_name = f"{cust_user.first_name}" if cust_user else "there"

    # Fetch past services
    past_q = await db.execute(
        select(Service.name, Service.category, Booking.scheduled_at)
        .join(Booking, Service.id == Booking.service_id)
        .where(
            Booking.customer_id == body.customer_id,
            Booking.status == BookingStatus.COMPLETED,
        )
        .order_by(Booking.scheduled_at.desc())
        .limit(5)
    )
    past_services = [{"name": r.name, "category": r.category, "date": str(r.scheduled_at)} for r in past_q.all()]

    # Build analysis points based on customer data
    analysis_points = []
    category_lower = body.service_category.lower()

    if category_lower in ("hair", "haircut", "hair styling", "hair colour", "hair color", "hair treatment"):
        if customer.hair_type:
            analysis_points.append(f"Hair type: {customer.hair_type}")
        if customer.hair_texture:
            analysis_points.append(f"Hair texture: {customer.hair_texture}")
        if customer.scalp_condition:
            analysis_points.append(f"Scalp condition: {customer.scalp_condition}")
        if customer.hair_damage_level:
            level = customer.hair_damage_level
            analysis_points.append(f"Damage level: {level}/10 ({'needs attention' if level >= 5 else 'healthy'})")
        if customer.current_hair_color:
            analysis_points.append(f"Current color: {customer.current_hair_color}")

    if category_lower in ("skin", "facial", "skincare", "skin care", "skin treatment"):
        if customer.skin_type:
            analysis_points.append(f"Skin type: {customer.skin_type}")
        if customer.skin_tone:
            analysis_points.append(f"Skin tone: {customer.skin_tone}")
        if customer.primary_skin_concerns:
            analysis_points.append(f"Primary concerns: {', '.join(customer.primary_skin_concerns)}")
        if customer.skin_sensitivity:
            analysis_points.append(f"Sensitivity: {customer.skin_sensitivity}")
        if customer.acne_severity:
            analysis_points.append(f"Acne severity: {customer.acne_severity}/10")

    if customer.stress_level:
        analysis_points.append(f"Stress level: {customer.stress_level}")

    # Build recommendations from available services
    services_q = await db.execute(
        select(Service)
        .where(
            Service.is_active == True,
            Service.category.ilike(f"%{body.service_category}%"),
        )
        .limit(5)
    )
    matching_services = services_q.scalars().all()

    recommendations = []
    for svc in matching_services:
        reason = f"Recommended based on your {body.service_category} profile"
        if customer.hair_damage_level and customer.hair_damage_level >= 5 and "treatment" in (svc.name or "").lower():
            reason = "Your hair shows signs of damage that this treatment can address"
        elif customer.primary_skin_concerns and "facial" in (svc.name or "").lower():
            reason = f"Targets your concerns: {', '.join(customer.primary_skin_concerns[:2])}"

        recommendations.append({
            "service_id": svc.id,
            "service": svc.name,
            "reason": reason,
            "price": float(svc.base_price),
        })

    # Things to avoid
    things_to_avoid = []
    if customer.known_allergies:
        things_to_avoid.append(f"ALLERGIES: Customer is allergic to {', '.join(customer.known_allergies)}")
    if customer.product_sensitivities:
        things_to_avoid.append(f"SENSITIVITIES: Avoid products with {', '.join(customer.product_sensitivities)}")
    if customer.hair_damage_level and customer.hair_damage_level >= 7:
        things_to_avoid.append("HIGH DAMAGE: Avoid chemical treatments until hair health improves")
    if customer.skin_sensitivity and customer.skin_sensitivity.lower() in ("high", "very high", "sensitive"):
        things_to_avoid.append("SENSITIVE SKIN: Avoid harsh exfoliants and strong actives")

    # Build greeting based on archetype
    archetype = customer.dominant_archetype
    greeting_style = ""
    if archetype:
        archetype_greetings = {
            "fire": f"Welcome back, {customer_name}! Ready to make a bold statement today?",
            "earth": f"So good to see you again, {customer_name}. Let's take care of you today.",
            "water": f"Welcome, {customer_name}. Let's create something beautiful and flowing today.",
            "air": f"Hi {customer_name}! I have some exciting new ideas I think you'll love.",
            "ether": f"Welcome to your sanctuary, {customer_name}. Let's make this session special.",
        }
        greeting_style = archetype_greetings.get(archetype.lower(), f"Welcome, {customer_name}! Great to have you here.")
    else:
        greeting_style = f"Welcome, {customer_name}! Great to have you here. Let me take a look at your profile."

    # Closing statement
    closing = "Let me know which option resonates with you, and we'll create the perfect plan together."
    if archetype and archetype.lower() == "fire":
        closing = "Which of these speaks to the bold, confident you? Let's make it happen!"
    elif archetype and archetype.lower() == "earth":
        closing = "Take your time deciding. We want to make sure you feel completely comfortable with the plan."

    return APIResponse(
        success=True,
        data={
            "customer_id": body.customer_id,
            "service_category": body.service_category,
            "consultation_script": {
                "greeting": greeting_style,
                "archetype": archetype,
                "analysis_points": analysis_points,
                "past_services_summary": past_services,
                "recommendations": recommendations,
                "things_to_avoid": things_to_avoid,
                "closing_statement": closing,
            },
            "customer_snapshot": {
                "total_visits": customer.total_visits,
                "beauty_score": customer.beauty_score,
                "primary_goal": customer.primary_goal,
                "goal_progress_pct": customer.goal_progress_pct,
            },
        },
    )


register_agent(AgentAction(
    name="ai_consultation_coach",
    description="Generate a personalized consultation coaching script with analysis, recommendations, and archetype-aware language",
    track="staff",
    feature="coaching",
    method="post",
    path="/agents/track2/staff/consultation-coach",
    handler=ai_consultation_coach_handler,
    roles=["stylist", "salon_manager"],
    ps_codes=["PS-02.07"],
    requires_ai=False,
))


# ─────────────────────────────────────────────────────────────
# 21. SKILL COMPETENCY CHECK  (PS-02.08)
# ─────────────────────────────────────────────────────────────

async def skill_competency_check_handler(
    staff_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "regional_manager", "super_admin"])),
):
    """Return a comprehensive skill map: levels, gaps, recommended trainings, service capabilities."""

    # Fetch staff
    staff_result = await db.execute(select(StaffProfile).where(StaffProfile.id == staff_id))
    staff = staff_result.scalar_one_or_none()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff profile not found")

    skill_levels_map = {"L1": 1, "L2": 2, "L3": 3}
    staff_level_num = skill_levels_map.get(enum_val(staff.skill_level) if staff.skill_level else "L1", 1)

    # Fetch all skill assessments for this staff
    assessments_q = await db.execute(
        select(SkillAssessment)
        .where(SkillAssessment.staff_id == staff_id)
        .order_by(SkillAssessment.created_at.desc())
    )
    assessments = assessments_q.scalars().all()

    # Group assessments by service category
    category_assessments = {}
    for a in assessments:
        cat = a.service_category or "general"
        if cat not in category_assessments:
            category_assessments[cat] = a  # Take the most recent one

    # Fetch all service categories
    categories_q = await db.execute(
        select(func.distinct(Service.category)).where(Service.is_active == True, Service.category.isnot(None))
    )
    all_categories = [row[0] for row in categories_q.all()]

    # Build skill map per category
    skill_map = []
    for category in all_categories:
        assessment = category_assessments.get(category)

        assessed_level = enum_val(assessment.current_level) if assessment and assessment.current_level else enum_val(staff.skill_level) if staff.skill_level else "L1"
        assessed_level_num = skill_levels_map.get(assessed_level, 1)
        score = float(assessment.score) if assessment and assessment.score else None

        # Gap items
        l2_gaps = list(assessment.l2_gap_items or []) if assessment else []
        l3_gaps = list(assessment.l3_gap_items or []) if assessment else []

        # Determine gap items for next level
        current_gaps = []
        if assessed_level_num == 1:
            current_gaps = l2_gaps if l2_gaps else ["Complete advanced training", "Pass L2 assessment"]
        elif assessed_level_num == 2:
            current_gaps = l3_gaps if l3_gaps else ["Master complex techniques", "Complete mentorship program"]

        # Recommended trainings
        recommended = list(assessment.recommended_training or []) if assessment else []

        # Services at this category the staff can/cannot do
        services_q = await db.execute(
            select(Service.id, Service.name, Service.skill_required)
            .where(Service.is_active == True, Service.category == category)
        )
        can_do = []
        cannot_do = []
        for svc in services_q.all():
            req_num = skill_levels_map.get(enum_val(svc.skill_required) if svc.skill_required else "L1", 1)
            entry = {"service_id": svc.id, "name": svc.name, "required_level": enum_val(svc.skill_required) if svc.skill_required else "L1"}
            if assessed_level_num >= req_num:
                can_do.append(entry)
            else:
                cannot_do.append(entry)

        skill_map.append({
            "category": category,
            "assessed_level": assessed_level,
            "assessment_score": score,
            "gap_items_for_next_level": current_gaps,
            "recommended_trainings": recommended,
            "services_can_do": can_do,
            "services_cannot_do": cannot_do,
            "soulskin_certified": assessment.soulskin_certified if assessment else staff.soulskin_certified,
        })

    # Fetch completed trainings
    trainings_q = await db.execute(
        select(TrainingRecord.service_category, func.count(TrainingRecord.id))
        .where(TrainingRecord.staff_id == staff_id, TrainingRecord.passed == True)
        .group_by(TrainingRecord.service_category)
    )
    trainings_by_category = {row[0]: row[1] for row in trainings_q.all()}

    return APIResponse(
        success=True,
        data={
            "staff_id": staff_id,
            "employee_id": staff.employee_id,
            "overall_skill_level": enum_val(staff.skill_level) if staff.skill_level else "L1",
            "total_services_done": staff.total_services_done,
            "current_rating": float(staff.current_rating or 0),
            "soulskin_certified": staff.soulskin_certified,
            "skill_map": skill_map,
            "trainings_completed_by_category": trainings_by_category,
            "total_assessments": len(assessments),
        },
    )


register_agent(AgentAction(
    name="skill_competency_check",
    description="Comprehensive skill map with levels, gaps, recommended trainings, and service capabilities per category",
    track="staff",
    feature="competency",
    method="get",
    path="/agents/track2/staff/competency",
    handler=skill_competency_check_handler,
    roles=["salon_manager", "regional_manager", "super_admin"],
    ps_codes=["PS-02.08"],
    requires_ai=False,
))


# ─────────────────────────────────────────────────────────────
# 22. CAPACITY REBALANCE  (PS-02.09)
# ─────────────────────────────────────────────────────────────

class CapacityRebalanceRequest(BaseModel):
    location_id: str
    absent_staff_ids: list[str]


async def capacity_rebalance_handler(
    body: CapacityRebalanceRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "regional_manager", "super_admin"])),
):
    """Rebalance today's bookings when staff members are absent."""

    today = date.today()
    day_start = datetime(today.year, today.month, today.day, 0, 0, 0, tzinfo=timezone.utc)
    day_end = day_start + timedelta(days=1)

    if not body.absent_staff_ids:
        return APIResponse(
            success=True,
            data={"rebalance_plan": [], "message": "No absent staff specified"},
        )

    # Find today's bookings assigned to absent staff
    affected_q = await db.execute(
        select(Booking, Service)
        .join(Service, Booking.service_id == Service.id)
        .where(
            Booking.location_id == body.location_id,
            Booking.stylist_id.in_(body.absent_staff_ids),
            Booking.scheduled_at >= day_start,
            Booking.scheduled_at < day_end,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED, BookingStatus.CHECKED_IN]),
        )
        .order_by(Booking.scheduled_at)
    )
    affected_bookings = affected_q.all()

    if not affected_bookings:
        return APIResponse(
            success=True,
            data={
                "location_id": body.location_id,
                "absent_staff_ids": body.absent_staff_ids,
                "rebalance_plan": [],
                "message": "No bookings affected by absent staff",
            },
        )

    # Get available replacements (exclude absent staff)
    replacements_q = await db.execute(
        select(StaffProfile)
        .where(
            StaffProfile.location_id == body.location_id,
            StaffProfile.is_available == True,
            ~StaffProfile.id.in_(body.absent_staff_ids),
        )
    )
    available_staff = replacements_q.scalars().all()

    skill_levels_map = {"L1": 1, "L2": 2, "L3": 3}
    staff_assignment_count = {s.id: 0 for s in available_staff}

    rebalance_plan = []
    unresolvable = []

    for booking, service in affected_bookings:
        required_level = skill_levels_map.get(enum_val(service.skill_required) if service.skill_required else "L1", 1)

        # Score replacements
        best_replacement = None
        best_score = -1

        for staff in available_staff:
            staff_level_num = skill_levels_map.get(enum_val(staff.skill_level) if staff.skill_level else "L1", 1)

            if staff_level_num < required_level:
                continue  # Skip unqualified

            if service.is_chemical and staff_level_num < 2:
                continue  # Chemical services require L2+

            # Score: skill match + specialization + load balance + rating
            score = 0
            score += 30 if staff_level_num >= required_level else 0
            staff_specs = {s.lower() for s in (staff.specializations or [])}
            if (service.category or "").lower() in staff_specs:
                score += 25
            score += max(0, 25 - staff_assignment_count.get(staff.id, 0) * 8)
            score += min(20, (float(staff.current_rating or 3) / 5.0) * 20)

            if score > best_score:
                best_score = score
                best_replacement = staff

        if best_replacement:
            staff_assignment_count[best_replacement.id] = staff_assignment_count.get(best_replacement.id, 0) + 1

            # Determine if customer should be notified (different stylist than preferred)
            customer_q = await db.execute(
                select(CustomerProfile.preferred_stylist_id)
                .where(CustomerProfile.id == booking.customer_id)
            )
            pref_stylist = customer_q.scalar_one_or_none()
            notify_customer = pref_stylist == booking.stylist_id  # Notify if absent stylist was their preferred

            match_quality = (
                "excellent" if best_score >= 80 else
                "good" if best_score >= 60 else
                "acceptable" if best_score >= 40 else
                "poor"
            )

            rebalance_plan.append({
                "booking_id": booking.id,
                "booking_number": booking.booking_number,
                "scheduled_at": str(booking.scheduled_at),
                "service_name": service.name,
                "original_stylist_id": booking.stylist_id,
                "replacement_stylist_id": best_replacement.id,
                "replacement_employee_id": best_replacement.employee_id,
                "replacement_skill_level": enum_val(best_replacement.skill_level) if best_replacement.skill_level else "L1",
                "match_quality": match_quality,
                "match_score": round(best_score, 1),
                "customer_notification_needed": notify_customer,
            })
        else:
            unresolvable.append({
                "booking_id": booking.id,
                "booking_number": booking.booking_number,
                "service_name": service.name,
                "reason": f"No available staff with {enum_val(service.skill_required) if service.skill_required else 'L1'}+ skill level",
            })

    return APIResponse(
        success=True,
        data={
            "location_id": body.location_id,
            "absent_staff_ids": body.absent_staff_ids,
            "affected_bookings_count": len(affected_bookings),
            "reassigned_count": len(rebalance_plan),
            "unresolvable_count": len(unresolvable),
            "rebalance_plan": rebalance_plan,
            "unresolvable_bookings": unresolvable,
            "staff_workload_after": [
                {"staff_id": sid, "assigned_count": count}
                for sid, count in staff_assignment_count.items()
                if count > 0
            ],
        },
    )


register_agent(AgentAction(
    name="capacity_rebalance",
    description="Rebalance bookings when staff are absent by matching replacements by skill and availability",
    track="staff",
    feature="scheduling",
    method="post",
    path="/agents/track2/staff/rebalance",
    handler=capacity_rebalance_handler,
    roles=["salon_manager", "regional_manager", "super_admin"],
    ps_codes=["PS-02.09"],
    requires_ai=False,
))


# ─────────────────────────────────────────────────────────────
# 23. PRODUCT GUIDANCE  (PS-02.10)
# ─────────────────────────────────────────────────────────────

async def product_guidance_handler(
    service_id: str = Query(...),
    customer_id: str = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager"])),
):
    """Return exact product instructions from SOP with allergy contraindication checks."""

    # Fetch service and its SOP
    svc_result = await db.execute(select(Service).where(Service.id == service_id))
    service = svc_result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    sop_result = await db.execute(
        select(SOP).where(SOP.service_id == service_id, SOP.is_current == True)
    )
    sop = sop_result.scalar_one_or_none()

    if not sop:
        return APIResponse(
            success=True,
            data={
                "service_id": service_id,
                "service_name": service.name,
                "products": [],
                "message": "No SOP with product instructions found for this service",
            },
        )

    # Fetch customer allergy info if customer_id provided
    customer_allergies = []
    customer_sensitivities = []
    if customer_id:
        cp_result = await db.execute(select(CustomerProfile).where(CustomerProfile.id == customer_id))
        customer = cp_result.scalar_one_or_none()
        if customer:
            customer_allergies = [a.lower() for a in (customer.known_allergies or [])]
            customer_sensitivities = [s.lower() for s in (customer.product_sensitivities or [])]

    # Extract product instructions from SOP
    products_required = sop.products_required or []
    chemical_ratios = sop.chemical_ratios or {}
    steps = sop.steps if isinstance(sop.steps, list) else sop.steps.get("steps", [])

    # Build product guidance from SOP steps and metadata
    product_instructions = []
    for product_name in products_required:
        product_lower = product_name.lower()

        # Check for allergy contraindication
        is_contraindicated = False
        contraindication_reason = None
        for allergy in customer_allergies:
            if allergy in product_lower or product_lower in allergy:
                is_contraindicated = True
                contraindication_reason = f"Customer has known allergy to '{allergy}'"
                break
        for sensitivity in customer_sensitivities:
            if sensitivity in product_lower or product_lower in sensitivity:
                is_contraindicated = True
                contraindication_reason = f"Customer has sensitivity to '{sensitivity}'"
                break

        # Look for product-specific ratios
        ratio = chemical_ratios.get(product_name) or chemical_ratios.get(product_lower)

        # Extract product-related instructions from steps
        application_instructions = []
        processing_time = None
        for step in steps:
            step_text = ""
            if isinstance(step, dict):
                step_text = (step.get("instructions", "") + " " + step.get("description", "")).lower()
                if product_lower in step_text:
                    application_instructions.append(step.get("instructions") or step.get("description", ""))
                    processing_time = processing_time or step.get("processing_time_minutes") or step.get("duration_minutes")
            elif isinstance(step, str):
                if product_lower in step.lower():
                    application_instructions.append(step)

        product_instructions.append({
            "product_name": product_name,
            "mixing_ratio": ratio,
            "quantity_ml": None,  # Would come from SOP step details
            "processing_time_minutes": processing_time,
            "application_method": "; ".join(application_instructions) if application_instructions else "Follow standard SOP instructions",
            "warnings": [],
            "is_contraindicated": is_contraindicated,
            "contraindication_reason": contraindication_reason,
        })

    # Add warnings for chemical services
    warnings = []
    if service.is_chemical:
        warnings.append("Chemical service: ensure patch test is completed before application")
        warnings.append("Wear protective gloves during application")
        warnings.append("Ensure adequate ventilation")

    contraindicated_count = sum(1 for p in product_instructions if p["is_contraindicated"])

    return APIResponse(
        success=True,
        data={
            "service_id": service_id,
            "service_name": service.name,
            "is_chemical": service.is_chemical,
            "sop_version": sop.version,
            "products": product_instructions,
            "total_products": len(product_instructions),
            "contraindicated_count": contraindicated_count,
            "has_contraindications": contraindicated_count > 0,
            "general_warnings": warnings,
            "customer_id": customer_id,
        },
    )


register_agent(AgentAction(
    name="product_guidance",
    description="Return product instructions from SOP with mixing ratios, timing, and allergy contraindication checks",
    track="staff",
    feature="product_guidance",
    method="get",
    path="/agents/track2/staff/product-guidance",
    handler=product_guidance_handler,
    roles=["stylist", "salon_manager"],
    ps_codes=["PS-02.10"],
    requires_ai=False,
))
