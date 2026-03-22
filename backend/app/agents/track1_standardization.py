"""Track 1: Service Standardization & Quality Assurance agents.

Covers PS-01.01 through PS-01.10 — pre-service consultation, SOP guidance,
quality scoring, complaint root-cause analysis, branch dashboards, safety gates,
time monitoring, and cross-branch benchmarking.
"""
from datetime import datetime, timezone, timedelta

from fastapi import Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func, case, and_, or_, cast, Float
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
from app.models.mood import MoodDetection
from app.models.soulskin import SoulskinSession
from app.models.queue import SmartQueueEntry, QueueStatus
from app.models.location import Location


# ─────────────────────────────────────────────────────────────
# 1. PRE-SERVICE CONSULTATION  (PS-01.01)
# ─────────────────────────────────────────────────────────────

class PreServiceConsultationRequest(BaseModel):
    customer_id: str
    service_id: str
    booking_id: str


async def pre_service_consultation_handler(
    body: PreServiceConsultationRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager"])),
):
    """Build a pre-service consultation checklist based on service type and customer profile."""

    # Fetch service details
    svc_result = await db.execute(select(Service).where(Service.id == body.service_id))
    service = svc_result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # Fetch customer profile for known allergies / hair / skin data
    cp_result = await db.execute(select(CustomerProfile).where(CustomerProfile.id == body.customer_id))
    customer = cp_result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer profile not found")

    # Fetch SOP pre-service checklist template if exists
    sop_result = await db.execute(
        select(SOP).where(SOP.service_id == body.service_id, SOP.is_current == True)
    )
    sop = sop_result.scalar_one_or_none()

    # Build checklist dynamically based on service category
    checklist_items = []
    category = (service.category or "").lower()

    # Common items for all services
    checklist_items.append({
        "key": "customer_confirmed_identity",
        "question": "Have you confirmed the customer's identity and booking details?",
        "required": True,
        "type": "boolean",
    })

    # Chemical service checks
    if service.is_chemical:
        checklist_items.extend([
            {
                "key": "allergy_check",
                "question": "Has the customer been asked about known allergies?",
                "required": True,
                "type": "boolean",
                "customer_known_allergies": customer.known_allergies or [],
            },
            {
                "key": "patch_test_done",
                "question": "Has a patch test been completed within the last 48 hours?",
                "required": True,
                "type": "boolean",
                "last_patch_test_date": str(customer.patch_tested_on) if customer.patch_tested_on else None,
                "last_patch_test_result": customer.patch_test_result,
            },
            {
                "key": "chemical_history_reviewed",
                "question": "Has the customer's chemical history been reviewed?",
                "required": True,
                "type": "boolean",
                "chemical_history": customer.chemical_history,
            },
            {
                "key": "hair_condition_check",
                "question": "Is the hair in suitable condition for chemical treatment?",
                "required": True,
                "type": "select",
                "options": ["excellent", "good", "fair", "poor"],
                "current_damage_level": customer.hair_damage_level,
            },
            {
                "key": "pregnancy_check",
                "question": "Has the customer confirmed they are not pregnant or breastfeeding?",
                "required": True,
                "type": "boolean",
            },
        ])

    # Hair service checks
    if category in ("hair", "haircut", "hair styling", "hair colour", "hair color", "hair treatment"):
        checklist_items.extend([
            {
                "key": "hair_type_confirmed",
                "question": "What is the customer's hair type?",
                "required": True,
                "type": "text",
                "prefilled": customer.hair_type,
            },
            {
                "key": "hair_texture_confirmed",
                "question": "What is the hair texture?",
                "required": False,
                "type": "text",
                "prefilled": customer.hair_texture,
            },
            {
                "key": "scalp_condition_check",
                "question": "What is the current scalp condition?",
                "required": True,
                "type": "select",
                "options": ["healthy", "dry", "oily", "flaky", "irritated", "sensitive"],
                "prefilled": customer.scalp_condition,
            },
            {
                "key": "desired_outcome",
                "question": "What is the customer's desired outcome for this service?",
                "required": True,
                "type": "text",
            },
        ])

    # Skin service checks
    if category in ("skin", "facial", "skin care", "skincare", "skin treatment"):
        checklist_items.extend([
            {
                "key": "skin_type_confirmed",
                "question": "What is the customer's skin type?",
                "required": True,
                "type": "select",
                "options": ["normal", "dry", "oily", "combination", "sensitive"],
                "prefilled": customer.skin_type,
            },
            {
                "key": "skin_concerns",
                "question": "What are the primary skin concerns?",
                "required": True,
                "type": "multi_select",
                "options": ["acne", "pigmentation", "aging", "dryness", "sensitivity", "dark circles", "sun damage"],
                "prefilled": customer.primary_skin_concerns,
            },
            {
                "key": "recent_treatments",
                "question": "Has the customer had any skin treatments in the last 2 weeks?",
                "required": True,
                "type": "boolean",
            },
            {
                "key": "sun_exposure_check",
                "question": "Has the customer had significant sun exposure recently?",
                "required": False,
                "type": "boolean",
            },
        ])

    # Merge SOP-defined checklist items if available
    if sop and sop.pre_service_checklist:
        sop_items = sop.pre_service_checklist.get("items", [])
        existing_keys = {item["key"] for item in checklist_items}
        for sop_item in sop_items:
            if sop_item.get("key") not in existing_keys:
                checklist_items.append(sop_item)

    # Allergy warning flag
    allergy_warning = bool(customer.known_allergies) and service.is_chemical

    return APIResponse(
        success=True,
        data={
            "booking_id": body.booking_id,
            "customer_id": body.customer_id,
            "service_id": body.service_id,
            "service_name": service.name,
            "service_category": service.category,
            "is_chemical": service.is_chemical,
            "allergy_warning": allergy_warning,
            "known_allergies": customer.known_allergies or [],
            "product_sensitivities": customer.product_sensitivities or [],
            "checklist_items": checklist_items,
            "total_items": len(checklist_items),
            "required_items": sum(1 for item in checklist_items if item.get("required")),
        },
    )


register_agent(AgentAction(
    name="pre_service_consultation",
    description="Generate a structured pre-service consultation checklist based on service type and customer profile",
    track="standardization",
    feature="consultation",
    method="post",
    path="/agents/track1/consultation/checklist",
    handler=pre_service_consultation_handler,
    roles=["stylist", "salon_manager"],
    ps_codes=["PS-01.01"],
    requires_ai=False,
))


# ─────────────────────────────────────────────────────────────
# 2. COMPLETE CONSULTATION  (PS-01.01)
# ─────────────────────────────────────────────────────────────

class CompleteConsultationRequest(BaseModel):
    booking_id: str
    checklist_responses: dict  # key -> value mapping


async def complete_consultation_handler(
    body: CompleteConsultationRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager"])),
):
    """Validate and record completed consultation checklist for a booking."""

    # Fetch session for this booking
    sess_result = await db.execute(
        select(ServiceSession).where(ServiceSession.booking_id == body.booking_id)
    )
    session = sess_result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Service session not found for this booking")

    if session.consultation_completed:
        raise HTTPException(status_code=400, detail="Consultation already completed for this session")

    # Fetch the booking to get service details
    bk_result = await db.execute(select(Booking).where(Booking.id == body.booking_id))
    booking = bk_result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Fetch service to check if chemical
    svc_result = await db.execute(select(Service).where(Service.id == booking.service_id))
    service = svc_result.scalar_one_or_none()

    # Rebuild expected checklist to validate required fields
    cp_result = await db.execute(select(CustomerProfile).where(CustomerProfile.id == booking.customer_id))
    customer = cp_result.scalar_one_or_none()

    # Determine required keys from the service type
    required_keys = ["customer_confirmed_identity"]
    if service and service.is_chemical:
        required_keys.extend(["allergy_check", "patch_test_done", "chemical_history_reviewed",
                              "hair_condition_check", "pregnancy_check"])

    # Validate all required items are answered
    missing_required = [key for key in required_keys if key not in body.checklist_responses]
    if missing_required:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required consultation items: {', '.join(missing_required)}",
        )

    # Block if chemical service and allergy check or patch test failed
    if service and service.is_chemical:
        allergy_ok = body.checklist_responses.get("allergy_check")
        patch_ok = body.checklist_responses.get("patch_test_done")
        hair_condition = body.checklist_responses.get("hair_condition_check")

        blocking_reasons = []
        if not allergy_ok:
            blocking_reasons.append("Allergy check not passed")
        if not patch_ok:
            blocking_reasons.append("Patch test not completed")
        if hair_condition == "poor":
            blocking_reasons.append("Hair condition too poor for chemical treatment")

        if blocking_reasons:
            return APIResponse(
                success=False,
                data={
                    "consultation_completed": False,
                    "blocked": True,
                    "blocking_reasons": blocking_reasons,
                },
                message="Consultation blocked due to safety concerns",
            )

    # Store checklist and mark completed
    now = datetime.now(timezone.utc)
    session.consultation_checklist = {
        "responses": body.checklist_responses,
        "completed_by": user.id,
        "completed_at": now.isoformat(),
    }
    session.consultation_completed = True
    session.consultation_completed_at = now
    await db.flush()

    return APIResponse(
        success=True,
        data={
            "booking_id": body.booking_id,
            "session_id": session.id,
            "consultation_completed": True,
            "blocked": False,
            "completed_at": now.isoformat(),
            "responses_count": len(body.checklist_responses),
        },
        message="Consultation completed successfully",
    )


register_agent(AgentAction(
    name="complete_consultation",
    description="Validate and record completed pre-service consultation responses",
    track="standardization",
    feature="consultation",
    method="post",
    path="/agents/track1/consultation/complete",
    handler=complete_consultation_handler,
    roles=["stylist", "salon_manager"],
    ps_codes=["PS-01.01"],
    requires_ai=False,
))


# ─────────────────────────────────────────────────────────────
# 3. SOP LIVE GUIDE  (PS-01.02)
# ─────────────────────────────────────────────────────────────

async def sop_live_guide_handler(
    session_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager"])),
):
    """Return current SOP step with full instructions for the active session."""

    sess_result = await db.execute(
        select(ServiceSession).where(ServiceSession.id == session_id)
    )
    session = sess_result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session.sop_id:
        raise HTTPException(status_code=400, detail="No SOP linked to this session")

    # Fetch the SOP
    sop_result = await db.execute(select(SOP).where(SOP.id == session.sop_id))
    sop = sop_result.scalar_one_or_none()
    if not sop:
        raise HTTPException(status_code=404, detail="SOP not found")

    steps = sop.steps if isinstance(sop.steps, list) else sop.steps.get("steps", [])
    total_steps = len(steps)
    current_step_num = session.current_step or 1

    if current_step_num < 1 or current_step_num > total_steps:
        raise HTTPException(status_code=400, detail=f"Invalid step number {current_step_num}")

    current_step = steps[current_step_num - 1]

    # Look up SOULSKIN overlay for customer archetype
    soulskin_overlay = None
    if session.archetype_applied and sop.soulskin_overlays:
        overlays = sop.soulskin_overlays
        soulskin_overlay = overlays.get(session.archetype_applied)

    # Build previous/next step info
    prev_step = steps[current_step_num - 2] if current_step_num > 1 else None
    next_step = steps[current_step_num] if current_step_num < total_steps else None

    return APIResponse(
        success=True,
        data={
            "session_id": session_id,
            "sop_id": sop.id,
            "sop_title": sop.title,
            "sop_version": sop.version,
            "total_steps": total_steps,
            "current_step_number": current_step_num,
            "steps_completed": session.steps_completed or [],
            "current_step": current_step,
            "products_required": sop.products_required or [],
            "chemicals_involved": sop.chemicals_involved,
            "chemical_ratios": sop.chemical_ratios,
            "soulskin_overlay": soulskin_overlay,
            "archetype_applied": session.archetype_applied,
            "prev_step": {"step_number": current_step_num - 1, "summary": prev_step} if prev_step else None,
            "next_step": {"step_number": current_step_num + 1, "summary": next_step} if next_step else None,
            "session_status": enum_val(session.status) if session.status else "unknown",
            "total_duration_minutes": sop.total_duration_minutes,
        },
    )


register_agent(AgentAction(
    name="sop_live_guide",
    description="Return current SOP step with full instructions, timer info, products, and SOULSKIN overlay",
    track="standardization",
    feature="sop",
    method="get",
    path="/agents/track1/sop/guide",
    handler=sop_live_guide_handler,
    roles=["stylist", "salon_manager"],
    ps_codes=["PS-01.02"],
    requires_ai=False,
    offline_capable=True,
))


# ─────────────────────────────────────────────────────────────
# 4. SOP STEP COMPLETE  (PS-01.02)
# ─────────────────────────────────────────────────────────────

class SOPStepCompleteRequest(BaseModel):
    session_id: str
    step_number: int
    photo_url: str | None = None


async def sop_step_complete_handler(
    body: SOPStepCompleteRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager"])),
):
    """Record completion of a single SOP step with timing analysis."""

    sess_result = await db.execute(
        select(ServiceSession).where(ServiceSession.id == body.session_id)
    )
    session = sess_result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session.sop_id:
        raise HTTPException(status_code=400, detail="No SOP linked to this session")

    # Fetch SOP
    sop_result = await db.execute(select(SOP).where(SOP.id == session.sop_id))
    sop = sop_result.scalar_one_or_none()
    if not sop:
        raise HTTPException(status_code=404, detail="SOP not found")

    steps = sop.steps if isinstance(sop.steps, list) else sop.steps.get("steps", [])
    total_steps = len(steps)

    if body.step_number < 1 or body.step_number > total_steps:
        raise HTTPException(status_code=400, detail=f"Step {body.step_number} is out of range (1-{total_steps})")

    step_def = steps[body.step_number - 1]
    now = datetime.now(timezone.utc)

    # Calculate time spent on this step
    completed_steps = list(session.steps_completed or [])
    is_rushing = False
    time_spent_seconds = None
    prescribed_time_minutes = step_def.get("duration_minutes") or step_def.get("time_minutes")

    if session.started_at:
        started = session.started_at if isinstance(session.started_at, datetime) else datetime.fromisoformat(str(session.started_at))
        if hasattr(started, 'tzinfo') and started.tzinfo is None:
            started = started.replace(tzinfo=timezone.utc)
        elapsed = (now - started).total_seconds()
        time_spent_seconds = elapsed

        if prescribed_time_minutes and prescribed_time_minutes > 0:
            prescribed_seconds = prescribed_time_minutes * 60
            # If step completed in less than 50% of prescribed time, flag as rushed
            if time_spent_seconds < prescribed_seconds * 0.5:
                is_rushing = True

    # Record the step completion
    if body.step_number not in completed_steps:
        completed_steps.append(body.step_number)

    session.steps_completed = sorted(completed_steps)
    session.current_step = min(body.step_number + 1, total_steps)

    # Build deviations record
    deviations = dict(session.deviations or {})
    step_key = f"step_{body.step_number}"
    deviations[step_key] = {
        "completed_at": now.isoformat(),
        "photo_url": body.photo_url,
        "is_rushing": is_rushing,
        "time_spent_seconds": time_spent_seconds,
        "prescribed_time_minutes": prescribed_time_minutes,
    }
    session.deviations = deviations

    # If all steps done, mark session completed
    all_done = len(completed_steps) >= total_steps
    if all_done:
        session.status = SessionStatus.COMPLETED
        session.completed_at = now

    # Update compliance percentage
    session.sop_compliance_pct = round((len(completed_steps) / total_steps) * 100, 1) if total_steps > 0 else 0

    await db.flush()

    return APIResponse(
        success=True,
        data={
            "session_id": body.session_id,
            "step_number": body.step_number,
            "step_completed": True,
            "is_rushing": is_rushing,
            "time_spent_seconds": time_spent_seconds,
            "prescribed_time_minutes": prescribed_time_minutes,
            "steps_completed_so_far": completed_steps,
            "total_steps": total_steps,
            "pct_complete": round((len(completed_steps) / total_steps) * 100, 1) if total_steps > 0 else 0,
            "all_steps_done": all_done,
            "session_status": enum_val(session.status) if session.status else "active",
        },
    )


register_agent(AgentAction(
    name="sop_step_complete",
    description="Record completion of an SOP step with timing and rushing analysis",
    track="standardization",
    feature="sop",
    method="post",
    path="/agents/track1/sop/step-complete",
    handler=sop_step_complete_handler,
    roles=["stylist", "salon_manager"],
    ps_codes=["PS-01.02"],
    requires_ai=False,
    offline_capable=True,
))


# ─────────────────────────────────────────────────────────────
# 5. QUALITY SCORE COMPUTE  (PS-01.03)
# ─────────────────────────────────────────────────────────────

class QualityScoreRequest(BaseModel):
    booking_id: str


async def quality_score_compute_handler(
    body: QualityScoreRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager", "regional_manager"])),
):
    """Compute an objective composite quality score from multiple signals."""

    # Fetch session
    sess_result = await db.execute(
        select(ServiceSession).where(ServiceSession.booking_id == body.booking_id)
    )
    session = sess_result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="No session found for this booking")

    # Fetch booking
    bk_result = await db.execute(select(Booking).where(Booking.id == body.booking_id))
    booking = bk_result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Fetch customer feedback
    fb_result = await db.execute(
        select(CustomerFeedback).where(CustomerFeedback.booking_id == body.booking_id)
    )
    feedback = fb_result.scalar_one_or_none()

    # ── Score components (each normalized to 0-100) ──

    # 1. SOP compliance (from session)
    sop_compliance = float(session.sop_compliance_pct or 0)

    # 2. Timing compliance
    timing_compliance = float(session.timing_compliance or 100)

    # 3. Customer feedback rating (scale 1-5 -> 0-100)
    customer_score = 0.0
    has_feedback = False
    if feedback:
        has_feedback = True
        customer_score = (float(feedback.overall_rating) / 5.0) * 100

    # 4. Before/after photo flag (binary bonus)
    has_photos = bool(session.before_image_url and session.after_image_url)
    photo_score = 100.0 if has_photos else 0.0

    # 5. Deviation count
    deviation_count = 0
    rushing_count = 0
    if session.deviations:
        devs = session.deviations
        deviation_count = len(devs)
        rushing_count = sum(1 for d in devs.values() if isinstance(d, dict) and d.get("is_rushing"))

    deviation_penalty = max(0, 100 - (deviation_count * 10) - (rushing_count * 15))

    # ── Weighted composite ──
    weights = {
        "sop_compliance": 0.30,
        "timing_compliance": 0.20,
        "customer_feedback": 0.25,
        "photo_documentation": 0.10,
        "deviation_penalty": 0.15,
    }

    composite = (
        sop_compliance * weights["sop_compliance"]
        + timing_compliance * weights["timing_compliance"]
        + (customer_score if has_feedback else 70) * weights["customer_feedback"]
        + photo_score * weights["photo_documentation"]
        + deviation_penalty * weights["deviation_penalty"]
    )
    composite = round(min(100, max(0, composite)), 1)

    # Save to session and create/update quality assessment
    session.quality_score = composite

    # Check for existing quality assessment
    qa_result = await db.execute(
        select(QualityAssessment).where(QualityAssessment.booking_id == body.booking_id)
    )
    qa = qa_result.scalar_one_or_none()
    if qa:
        qa.sop_compliance_score = sop_compliance
        qa.timing_score = timing_compliance
        qa.customer_rating = feedback.overall_rating if feedback else None
        qa.overall_score = composite
        qa.is_flagged = composite < 60
        qa.flag_reason = "Low quality score" if composite < 60 else None
    else:
        qa = QualityAssessment(
            booking_id=body.booking_id,
            session_id=session.id,
            stylist_id=booking.stylist_id,
            location_id=booking.location_id,
            service_id=booking.service_id,
            sop_compliance_score=sop_compliance,
            timing_score=timing_compliance,
            customer_rating=feedback.overall_rating if feedback else None,
            overall_score=composite,
            before_image_url=session.before_image_url,
            after_image_url=session.after_image_url,
            is_flagged=composite < 60,
            flag_reason="Low quality score" if composite < 60 else None,
        )
        db.add(qa)

    await db.flush()

    return APIResponse(
        success=True,
        data={
            "booking_id": body.booking_id,
            "composite_score": composite,
            "breakdown": {
                "sop_compliance": {"score": sop_compliance, "weight": weights["sop_compliance"]},
                "timing_compliance": {"score": timing_compliance, "weight": weights["timing_compliance"]},
                "customer_feedback": {
                    "score": customer_score if has_feedback else None,
                    "weight": weights["customer_feedback"],
                    "has_feedback": has_feedback,
                    "default_used": not has_feedback,
                },
                "photo_documentation": {"score": photo_score, "weight": weights["photo_documentation"], "has_photos": has_photos},
                "deviation_penalty": {
                    "score": deviation_penalty,
                    "weight": weights["deviation_penalty"],
                    "deviation_count": deviation_count,
                    "rushing_count": rushing_count,
                },
            },
            "is_flagged": composite < 60,
            "quality_label": (
                "excellent" if composite >= 90 else
                "good" if composite >= 75 else
                "average" if composite >= 60 else
                "needs_improvement"
            ),
        },
    )


register_agent(AgentAction(
    name="quality_score_compute",
    description="Compute objective quality score from SOP compliance, timing, feedback, photos, and deviations",
    track="standardization",
    feature="quality",
    method="post",
    path="/agents/track1/quality/compute",
    handler=quality_score_compute_handler,
    roles=["stylist", "salon_manager", "regional_manager"],
    ps_codes=["PS-01.03"],
    requires_ai=False,
))


# ─────────────────────────────────────────────────────────────
# 6. COMPLAINT ROOT CAUSE  (PS-01.04)
# ─────────────────────────────────────────────────────────────

class ComplaintRootCauseRequest(BaseModel):
    booking_id: str
    complaint_text: str


async def complaint_root_cause_handler(
    body: ComplaintRootCauseRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "regional_manager", "super_admin"])),
):
    """Analyze root cause of a complaint by correlating SOP deviations, products, and timings."""

    # Fetch booking
    bk_result = await db.execute(select(Booking).where(Booking.id == body.booking_id))
    booking = bk_result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Fetch session
    sess_result = await db.execute(
        select(ServiceSession).where(ServiceSession.booking_id == body.booking_id)
    )
    session = sess_result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="No session found for this booking")

    # Fetch service
    svc_result = await db.execute(select(Service).where(Service.id == booking.service_id))
    service = svc_result.scalar_one_or_none()

    # Fetch SOP
    sop = None
    if session.sop_id:
        sop_result = await db.execute(select(SOP).where(SOP.id == session.sop_id))
        sop = sop_result.scalar_one_or_none()

    # Analyze deviations
    deviations = session.deviations or {}
    deviation_steps = []
    rushed_steps = []
    for step_key, dev_data in deviations.items():
        if isinstance(dev_data, dict):
            step_num = step_key.replace("step_", "")
            if dev_data.get("is_rushing"):
                rushed_steps.append(step_num)
            deviation_steps.append({
                "step": step_num,
                "completed_at": dev_data.get("completed_at"),
                "is_rushing": dev_data.get("is_rushing", False),
                "time_spent_seconds": dev_data.get("time_spent_seconds"),
                "prescribed_time_minutes": dev_data.get("prescribed_time_minutes"),
            })

    # Products analysis
    products_used = session.products_used or {}
    chemical_ratios_used = session.chemical_ratios_used or {}
    chemical_ratios_expected = sop.chemical_ratios if sop else {}

    # Detect chemical ratio mismatch
    ratio_mismatch = False
    mismatched_chemicals = []
    if chemical_ratios_expected and chemical_ratios_used:
        for chemical, expected_ratio in chemical_ratios_expected.items():
            actual_ratio = chemical_ratios_used.get(chemical)
            if actual_ratio and actual_ratio != expected_ratio:
                ratio_mismatch = True
                mismatched_chemicals.append({
                    "chemical": chemical,
                    "expected_ratio": expected_ratio,
                    "actual_ratio": actual_ratio,
                })

    # Determine probable cause
    probable_cause = "undetermined"
    probable_step = None
    product_involved = None
    recommended_action = "Investigate further"

    if rushed_steps:
        probable_cause = "rushing_during_service"
        probable_step = rushed_steps[0]
        recommended_action = "Review SOP timing compliance. Provide coaching on time management."
    elif ratio_mismatch:
        probable_cause = "incorrect_chemical_ratios"
        product_involved = mismatched_chemicals[0]["chemical"] if mismatched_chemicals else None
        recommended_action = "Re-train on chemical mixing protocols. Verify measuring tools."
    elif float(session.sop_compliance_pct or 100) < 70:
        probable_cause = "low_sop_compliance"
        recommended_action = "Mandatory SOP refresher training required."
    elif deviation_steps:
        probable_cause = "sop_deviation"
        probable_step = deviation_steps[0]["step"]
        recommended_action = "Review specific step deviations with stylist."

    return APIResponse(
        success=True,
        data={
            "booking_id": body.booking_id,
            "complaint_text": body.complaint_text,
            "root_cause_analysis": {
                "probable_cause": probable_cause,
                "probable_step": probable_step,
                "stylist_id": booking.stylist_id,
                "service_name": service.name if service else None,
                "product_involved": product_involved,
                "recommended_action": recommended_action,
            },
            "deviation_details": deviation_steps,
            "rushed_steps": rushed_steps,
            "chemical_ratio_mismatch": ratio_mismatch,
            "mismatched_chemicals": mismatched_chemicals,
            "sop_compliance_pct": float(session.sop_compliance_pct or 0),
            "quality_score": float(session.quality_score or 0),
            "products_used": products_used,
        },
    )


register_agent(AgentAction(
    name="complaint_root_cause",
    description="Analyze complaint root cause by correlating SOP deviations, products, and timings",
    track="standardization",
    feature="quality",
    method="post",
    path="/agents/track1/quality/root-cause",
    handler=complaint_root_cause_handler,
    roles=["salon_manager", "regional_manager", "super_admin"],
    ps_codes=["PS-01.04"],
    requires_ai=False,
))


# ─────────────────────────────────────────────────────────────
# 7. BRANCH LIVE STATUS  (PS-01.05)
# ─────────────────────────────────────────────────────────────

async def branch_live_status_handler(
    location_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "regional_manager", "franchise_owner", "super_admin"])),
):
    """Return real-time branch dashboard with session, queue, staff, and revenue data."""

    # Verify location exists
    loc_result = await db.execute(select(Location).where(Location.id == location_id))
    location = loc_result.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    # Active sessions count (in_progress bookings at this location)
    active_sessions_q = await db.execute(
        select(func.count(ServiceSession.id))
        .join(Booking, ServiceSession.booking_id == Booking.id)
        .where(
            Booking.location_id == location_id,
            ServiceSession.status == SessionStatus.ACTIVE,
        )
    )
    active_sessions = active_sessions_q.scalar() or 0

    # Services in progress with step info
    in_progress_q = await db.execute(
        select(
            ServiceSession.id,
            ServiceSession.current_step,
            ServiceSession.steps_total,
            ServiceSession.started_at,
            ServiceSession.sop_compliance_pct,
            Booking.stylist_id,
            Service.name.label("service_name"),
        )
        .join(Booking, ServiceSession.booking_id == Booking.id)
        .join(Service, Booking.service_id == Service.id)
        .where(
            Booking.location_id == location_id,
            ServiceSession.status == SessionStatus.ACTIVE,
        )
    )
    services_in_progress = []
    for row in in_progress_q.all():
        services_in_progress.append({
            "session_id": row.id,
            "service_name": row.service_name,
            "stylist_id": row.stylist_id,
            "current_step": row.current_step,
            "steps_total": row.steps_total,
            "started_at": str(row.started_at) if row.started_at else None,
            "sop_compliance_pct": float(row.sop_compliance_pct) if row.sop_compliance_pct else None,
        })

    # Queue length and avg wait time
    queue_q = await db.execute(
        select(
            func.count(SmartQueueEntry.id).label("queue_length"),
            func.avg(SmartQueueEntry.estimated_wait_mins).label("avg_wait"),
        )
        .where(
            SmartQueueEntry.location_id == location_id,
            SmartQueueEntry.status == QueueStatus.WAITING,
        )
    )
    queue_row = queue_q.one()
    queue_length = queue_row.queue_length or 0
    avg_wait_time = round(float(queue_row.avg_wait or 0), 1)

    # Stylists available at this location
    staff_q = await db.execute(
        select(func.count(StaffProfile.id))
        .where(
            StaffProfile.location_id == location_id,
            StaffProfile.is_available == True,
        )
    )
    stylists_available = staff_q.scalar() or 0

    # Quality flags today (flagged quality assessments)
    flags_q = await db.execute(
        select(func.count(QualityAssessment.id))
        .where(
            QualityAssessment.location_id == location_id,
            QualityAssessment.is_flagged == True,
            QualityAssessment.created_at >= today_start,
        )
    )
    quality_flags_today = flags_q.scalar() or 0

    # Revenue today (completed bookings)
    revenue_q = await db.execute(
        select(func.coalesce(func.sum(Booking.final_price), 0))
        .where(
            Booking.location_id == location_id,
            Booking.status == BookingStatus.COMPLETED,
            Booking.actual_end_at >= today_start,
        )
    )
    revenue_today = float(revenue_q.scalar() or 0)

    return APIResponse(
        success=True,
        data={
            "location_id": location_id,
            "location_name": location.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "active_sessions": active_sessions,
            "queue_length": queue_length,
            "avg_wait_time_minutes": avg_wait_time,
            "stylists_available": stylists_available,
            "services_in_progress": services_in_progress,
            "quality_flags_today": quality_flags_today,
            "revenue_today": revenue_today,
            "seating_capacity": location.seating_capacity,
            "occupancy_pct": round((active_sessions / location.seating_capacity) * 100, 1) if location.seating_capacity else 0,
        },
    )


register_agent(AgentAction(
    name="branch_live_status",
    description="Real-time branch dashboard: sessions, queue, staff, revenue, quality flags",
    track="standardization",
    feature="branch_ops",
    method="get",
    path="/agents/track1/branch/live-status",
    handler=branch_live_status_handler,
    roles=["salon_manager", "regional_manager", "franchise_owner", "super_admin"],
    ps_codes=["PS-01.05"],
    requires_ai=False,
))


# ─────────────────────────────────────────────────────────────
# 8. SERVICE READINESS CHECK  (PS-01.06)
# ─────────────────────────────────────────────────────────────

async def service_readiness_check_handler(
    location_id: str = Query(...),
    service_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "regional_manager", "super_admin"])),
):
    """Check if a location is ready to offer a specific service: trained staff, SOP, quality scores."""

    # Verify location
    loc_result = await db.execute(select(Location).where(Location.id == location_id))
    location = loc_result.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    # Fetch service
    svc_result = await db.execute(select(Service).where(Service.id == service_id))
    service = svc_result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    blockers = []

    # 1. Trained stylists with matching skill level
    required_level = service.skill_required  # e.g. SkillLevel.L2
    skill_levels_map = {"L1": 1, "L2": 2, "L3": 3}
    required_numeric = skill_levels_map.get(enum_val(required_level) if required_level else "L1", 1)

    # Query staff at this location with sufficient skill level
    staff_q = await db.execute(
        select(StaffProfile)
        .where(
            StaffProfile.location_id == location_id,
            StaffProfile.is_available == True,
        )
    )
    all_staff = staff_q.scalars().all()
    trained_staff = []
    for s in all_staff:
        staff_level_numeric = skill_levels_map.get(enum_val(s.skill_level) if s.skill_level else "L1", 1)
        if staff_level_numeric >= required_numeric:
            trained_staff.append({
                "staff_id": s.id,
                "skill_level": enum_val(s.skill_level) if s.skill_level else "L1",
                "employee_id": s.employee_id,
            })

    if len(trained_staff) == 0:
        blockers.append(f"No staff with skill level {enum_val(required_level) if required_level else 'L1'} or above at this location")

    # 2. SOP exists for service
    sop_q = await db.execute(
        select(SOP).where(SOP.service_id == service_id, SOP.is_current == True)
    )
    sop = sop_q.scalar_one_or_none()
    has_sop = sop is not None
    if not has_sop:
        blockers.append("No current SOP defined for this service")

    # 3. Recent quality scores for this service at this location (last 30 days)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    quality_q = await db.execute(
        select(
            func.count(QualityAssessment.id).label("count"),
            func.avg(QualityAssessment.overall_score).label("avg_score"),
            func.min(QualityAssessment.overall_score).label("min_score"),
        )
        .where(
            QualityAssessment.location_id == location_id,
            QualityAssessment.service_id == service_id,
            QualityAssessment.created_at >= thirty_days_ago,
        )
    )
    quality_row = quality_q.one()
    quality_count = quality_row.count or 0
    avg_quality = round(float(quality_row.avg_score or 0), 1) if quality_row.avg_score else None
    min_quality = round(float(quality_row.min_score or 0), 1) if quality_row.min_score else None

    if avg_quality is not None and avg_quality < 60:
        blockers.append(f"Average quality score for this service is below threshold ({avg_quality}/100)")

    # Compute readiness score
    readiness_components = []
    readiness_components.append(min(40, len(trained_staff) * 20))  # up to 40 points for trained staff
    readiness_components.append(30 if has_sop else 0)  # 30 points for SOP
    readiness_components.append(
        min(30, (avg_quality / 100) * 30) if avg_quality else 15  # up to 30 points for quality; 15 default
    )
    readiness_score = round(sum(readiness_components), 1)

    return APIResponse(
        success=True,
        data={
            "location_id": location_id,
            "location_name": location.name,
            "service_id": service_id,
            "service_name": service.name,
            "service_category": service.category,
            "skill_required": enum_val(required_level) if required_level else "L1",
            "readiness_score": readiness_score,
            "readiness_label": (
                "ready" if readiness_score >= 70 and not blockers else
                "partial" if readiness_score >= 40 else
                "not_ready"
            ),
            "blockers": blockers,
            "trained_staff_count": len(trained_staff),
            "trained_staff": trained_staff,
            "has_sop": has_sop,
            "sop_version": sop.version if sop else None,
            "quality_stats_30d": {
                "assessment_count": quality_count,
                "avg_score": avg_quality,
                "min_score": min_quality,
            },
        },
    )


register_agent(AgentAction(
    name="service_readiness_check",
    description="Check if a location has trained staff, SOPs, and quality scores for a service",
    track="standardization",
    feature="branch_ops",
    method="get",
    path="/agents/track1/branch/readiness",
    handler=service_readiness_check_handler,
    roles=["salon_manager", "regional_manager", "super_admin"],
    ps_codes=["PS-01.06"],
    requires_ai=False,
))


# ─────────────────────────────────────────────────────────────
# 9. CUSTOMER HANDOVER BRIEF  (PS-01.07)
# ─────────────────────────────────────────────────────────────

async def customer_handover_brief_handler(
    customer_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager"])),
):
    """Return complete handover brief: recent services, allergies, preferences, archetype, moods."""

    # Fetch customer profile
    cp_result = await db.execute(select(CustomerProfile).where(CustomerProfile.id == customer_id))
    customer = cp_result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer profile not found")

    # Last 5 services with outcomes
    recent_bookings_q = await db.execute(
        select(
            Booking.id,
            Booking.scheduled_at,
            Booking.status,
            Booking.stylist_id,
            Booking.notes,
            Service.name.label("service_name"),
            Service.category.label("service_category"),
        )
        .join(Service, Booking.service_id == Service.id)
        .where(Booking.customer_id == customer_id)
        .order_by(Booking.scheduled_at.desc())
        .limit(5)
    )
    recent_services = []
    for row in recent_bookings_q.all():
        # Fetch quality score for each booking
        qa_q = await db.execute(
            select(QualityAssessment.overall_score)
            .where(QualityAssessment.booking_id == row.id)
        )
        qa_score = qa_q.scalar_one_or_none()

        # Fetch feedback
        fb_q = await db.execute(
            select(CustomerFeedback.overall_rating, CustomerFeedback.comment)
            .where(CustomerFeedback.booking_id == row.id)
        )
        fb_row = fb_q.one_or_none()

        recent_services.append({
            "booking_id": row.id,
            "service_name": row.service_name,
            "category": row.service_category,
            "scheduled_at": str(row.scheduled_at),
            "status": enum_val(row.status) if row.status else None,
            "stylist_id": row.stylist_id,
            "notes": row.notes,
            "quality_score": float(qa_score) if qa_score else None,
            "customer_rating": fb_row.overall_rating if fb_row else None,
            "customer_comment": fb_row.comment if fb_row else None,
        })

    # Mood history (last 5)
    mood_q = await db.execute(
        select(MoodDetection)
        .where(MoodDetection.customer_id == customer_id)
        .order_by(MoodDetection.created_at.desc())
        .limit(5)
    )
    mood_history = [
        {
            "detected_emotion": m.detected_emotion,
            "energy_level": m.energy_level,
            "recommended_archetype": m.recommended_archetype,
            "captured_at": str(m.captured_at) if m.captured_at else str(m.created_at),
        }
        for m in mood_q.scalars().all()
    ]

    # SOULSKIN archetype history
    soulskin_q = await db.execute(
        select(SoulskinSession.archetype, SoulskinSession.created_at)
        .where(
            SoulskinSession.customer_id == customer_id,
            SoulskinSession.session_completed == True,
        )
        .order_by(SoulskinSession.created_at.desc())
        .limit(3)
    )
    archetype_sessions = [
        {"archetype": row.archetype, "date": str(row.created_at)}
        for row in soulskin_q.all()
    ]

    # Preferred stylist info
    preferred_stylist_info = None
    if customer.preferred_stylist_id:
        ps_q = await db.execute(
            select(StaffProfile.id, StaffProfile.employee_id, StaffProfile.specializations,
                   User.first_name, User.last_name)
            .join(User, StaffProfile.user_id == User.id)
            .where(StaffProfile.id == customer.preferred_stylist_id)
        )
        ps_row = ps_q.one_or_none()
        if ps_row:
            preferred_stylist_info = {
                "staff_id": ps_row.id,
                "employee_id": ps_row.employee_id,
                "name": f"{ps_row.first_name} {ps_row.last_name}",
                "specializations": ps_row.specializations,
            }

    return APIResponse(
        success=True,
        data={
            "customer_id": customer_id,
            "recent_services": recent_services,
            "known_allergies": customer.known_allergies or [],
            "product_sensitivities": customer.product_sensitivities or [],
            "hair_profile": {
                "hair_type": customer.hair_type,
                "hair_texture": customer.hair_texture,
                "hair_porosity": customer.hair_porosity,
                "scalp_condition": customer.scalp_condition,
                "damage_level": customer.hair_damage_level,
                "current_color": customer.current_hair_color,
            },
            "skin_profile": {
                "skin_type": customer.skin_type,
                "skin_tone": customer.skin_tone,
                "skin_sensitivity": customer.skin_sensitivity,
                "primary_concerns": customer.primary_skin_concerns,
            },
            "soulskin": {
                "dominant_archetype": customer.dominant_archetype,
                "archetype_history": archetype_sessions,
                "emotional_sensitivity": customer.emotional_sensitivity,
                "preferred_touch_pressure": customer.preferred_touch_pressure,
            },
            "mood_history": mood_history,
            "preferred_stylist": preferred_stylist_info,
            "communication_preferences": {
                "preferred_language": None,  # from User model, not joined here for brevity
                "stress_level": customer.stress_level,
            },
            "beauty_score": customer.beauty_score,
            "total_visits": customer.total_visits,
            "lifetime_value": float(customer.lifetime_value) if customer.lifetime_value else 0,
        },
    )


register_agent(AgentAction(
    name="customer_handover_brief",
    description="Complete customer handover brief with services, allergies, archetype, mood, and preferences",
    track="standardization",
    feature="handover",
    method="get",
    path="/agents/track1/handover/brief",
    handler=customer_handover_brief_handler,
    roles=["stylist", "salon_manager"],
    ps_codes=["PS-01.07"],
    requires_ai=False,
))


# ─────────────────────────────────────────────────────────────
# 10. CHEMICAL SAFETY GATE  (PS-01.08)
# ─────────────────────────────────────────────────────────────

class ChemicalSafetyGateRequest(BaseModel):
    booking_id: str
    service_id: str


async def chemical_safety_gate_handler(
    body: ChemicalSafetyGateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager"])),
):
    """Verify chemical safety prerequisites before proceeding with a chemical service."""

    # Fetch service
    svc_result = await db.execute(select(Service).where(Service.id == body.service_id))
    service = svc_result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    if not service.is_chemical:
        return APIResponse(
            success=True,
            data={
                "booking_id": body.booking_id,
                "service_id": body.service_id,
                "is_chemical": False,
                "gate_passed": True,
                "message": "Service is not a chemical service, no safety gate required",
            },
        )

    # Fetch booking
    bk_result = await db.execute(select(Booking).where(Booking.id == body.booking_id))
    booking = bk_result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Fetch customer profile
    cp_result = await db.execute(select(CustomerProfile).where(CustomerProfile.id == booking.customer_id))
    customer = cp_result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Fetch session for consultation data
    sess_result = await db.execute(
        select(ServiceSession).where(ServiceSession.booking_id == body.booking_id)
    )
    session = sess_result.scalar_one_or_none()

    blocking_reasons = []
    checks = {}

    # 1. Patch test done
    patch_test_done = False
    if customer.patch_tested_on:
        patch_date = customer.patch_tested_on if isinstance(customer.patch_tested_on, datetime) else None
        # Check if patch test was within last 48 hours
        if patch_date:
            hours_since = (datetime.now(timezone.utc) - patch_date).total_seconds() / 3600
            patch_test_done = hours_since <= 48
    # Also check consultation checklist
    if session and session.consultation_checklist:
        responses = session.consultation_checklist.get("responses", {})
        if responses.get("patch_test_done"):
            patch_test_done = True
    checks["patch_test_done"] = patch_test_done
    if not patch_test_done:
        blocking_reasons.append("Patch test not completed or expired (must be within 48 hours)")

    # 2. Allergy check passed
    allergy_check_passed = True
    if customer.known_allergies:
        # If customer has known allergies, check consultation confirmed it's safe
        if session and session.consultation_checklist:
            responses = session.consultation_checklist.get("responses", {})
            allergy_check_passed = bool(responses.get("allergy_check"))
        else:
            allergy_check_passed = False
    checks["allergy_check_passed"] = allergy_check_passed
    if not allergy_check_passed:
        blocking_reasons.append(f"Allergy check not passed. Known allergies: {', '.join(customer.known_allergies or [])}")

    # 3. Hair condition OK (damage level should be < 8 on 1-10 scale)
    hair_condition_ok = True
    if customer.hair_damage_level is not None and customer.hair_damage_level >= 8:
        hair_condition_ok = False
        blocking_reasons.append(f"Hair damage level too high ({customer.hair_damage_level}/10) for chemical treatment")
    checks["hair_condition_ok"] = hair_condition_ok

    # 4. Consultation completed
    consultation_done = session.consultation_completed if session else False
    checks["consultation_completed"] = consultation_done
    if not consultation_done:
        blocking_reasons.append("Pre-service consultation not completed")

    gate_passed = len(blocking_reasons) == 0

    # Record safety verification on session
    if session and gate_passed:
        session.chemical_safety_verified = True
        session.chemical_safety_verified_at = datetime.now(timezone.utc)
        session.chemical_safety_verified_by = user.id
        await db.flush()

    return APIResponse(
        success=True,
        data={
            "booking_id": body.booking_id,
            "service_id": body.service_id,
            "service_name": service.name,
            "is_chemical": True,
            "gate_passed": gate_passed,
            "blocking_reasons": blocking_reasons,
            "checks": checks,
            "customer_allergies": customer.known_allergies or [],
            "customer_damage_level": customer.hair_damage_level,
            "patch_test_date": str(customer.patch_tested_on) if customer.patch_tested_on else None,
            "patch_test_result": customer.patch_test_result,
        },
    )


register_agent(AgentAction(
    name="chemical_safety_gate",
    description="Verify chemical safety prerequisites: patch test, allergy check, hair condition",
    track="standardization",
    feature="safety",
    method="post",
    path="/agents/track1/safety/chemical-gate",
    handler=chemical_safety_gate_handler,
    roles=["stylist", "salon_manager"],
    ps_codes=["PS-01.08"],
    requires_ai=False,
))


# ─────────────────────────────────────────────────────────────
# 11. SERVICE TIME MONITOR  (PS-01.09)
# ─────────────────────────────────────────────────────────────

async def service_time_monitor_handler(
    location_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "regional_manager", "super_admin"])),
):
    """Monitor all active sessions at a location for timing compliance and rushing."""

    # Fetch all active sessions at this location
    sessions_q = await db.execute(
        select(
            ServiceSession.id,
            ServiceSession.booking_id,
            ServiceSession.started_at,
            ServiceSession.current_step,
            ServiceSession.steps_total,
            ServiceSession.steps_completed,
            ServiceSession.sop_compliance_pct,
            Booking.stylist_id,
            Service.name.label("service_name"),
            Service.duration_minutes.label("expected_duration"),
            SOP.total_duration_minutes.label("sop_duration"),
        )
        .join(Booking, ServiceSession.booking_id == Booking.id)
        .join(Service, Booking.service_id == Service.id)
        .outerjoin(SOP, ServiceSession.sop_id == SOP.id)
        .where(
            Booking.location_id == location_id,
            ServiceSession.status == SessionStatus.ACTIVE,
        )
    )

    now = datetime.now(timezone.utc)
    active_sessions = []

    for row in sessions_q.all():
        expected_minutes = row.sop_duration or row.expected_duration or 60
        actual_elapsed_minutes = 0
        if row.started_at:
            started = row.started_at if isinstance(row.started_at, datetime) else datetime.fromisoformat(str(row.started_at))
            if hasattr(started, 'tzinfo') and started.tzinfo is None:
                started = started.replace(tzinfo=timezone.utc)
            actual_elapsed_minutes = round((now - started).total_seconds() / 60, 1)

        completed_steps = row.steps_completed or []
        total_steps = row.steps_total or 1
        pct_steps_done = round((len(completed_steps) / total_steps) * 100, 1) if total_steps > 0 else 0
        pct_time_elapsed = round((actual_elapsed_minutes / expected_minutes) * 100, 1) if expected_minutes > 0 else 0

        # Rushing detection: if time < 60% expected and steps > 80% done
        is_rushing = (
            pct_time_elapsed < 60
            and pct_steps_done > 80
            and actual_elapsed_minutes > 5  # ignore very early sessions
        )

        # Overtime detection
        is_overtime = actual_elapsed_minutes > expected_minutes * 1.2  # 20% over

        active_sessions.append({
            "session_id": row.id,
            "booking_id": row.booking_id,
            "service_name": row.service_name,
            "stylist_id": row.stylist_id,
            "expected_duration_minutes": expected_minutes,
            "actual_elapsed_minutes": actual_elapsed_minutes,
            "pct_time_elapsed": pct_time_elapsed,
            "steps_completed": len(completed_steps),
            "steps_total": total_steps,
            "pct_steps_done": pct_steps_done,
            "is_rushing": is_rushing,
            "is_overtime": is_overtime,
            "sop_compliance_pct": float(row.sop_compliance_pct) if row.sop_compliance_pct else None,
            "started_at": str(row.started_at) if row.started_at else None,
        })

    rushing_count = sum(1 for s in active_sessions if s["is_rushing"])
    overtime_count = sum(1 for s in active_sessions if s["is_overtime"])

    return APIResponse(
        success=True,
        data={
            "location_id": location_id,
            "timestamp": now.isoformat(),
            "total_active_sessions": len(active_sessions),
            "rushing_count": rushing_count,
            "overtime_count": overtime_count,
            "sessions": active_sessions,
        },
    )


register_agent(AgentAction(
    name="service_time_monitor",
    description="Monitor active sessions for timing compliance, rushing, and overtime",
    track="standardization",
    feature="branch_ops",
    method="get",
    path="/agents/track1/branch/time-monitor",
    handler=service_time_monitor_handler,
    roles=["salon_manager", "regional_manager", "super_admin"],
    ps_codes=["PS-01.09"],
    requires_ai=False,
))


# ─────────────────────────────────────────────────────────────
# 12. CROSS-BRANCH BENCHMARK  (PS-01.10)
# ─────────────────────────────────────────────────────────────

async def cross_branch_benchmark_handler(
    service_id: str = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["regional_manager", "franchise_owner", "super_admin"])),
):
    """Benchmark performance across locations: quality, timing, complaints, revenue."""

    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)

    # Base filter
    quality_filters = [QualityAssessment.created_at >= thirty_days_ago]
    booking_filters = [Booking.created_at >= thirty_days_ago]
    if service_id:
        quality_filters.append(QualityAssessment.service_id == service_id)
        booking_filters.append(Booking.service_id == service_id)

    # Per-location quality scores
    quality_q = await db.execute(
        select(
            QualityAssessment.location_id,
            func.avg(QualityAssessment.overall_score).label("avg_quality"),
            func.count(QualityAssessment.id).label("assessment_count"),
        )
        .where(*quality_filters)
        .group_by(QualityAssessment.location_id)
    )
    quality_by_location = {row.location_id: {
        "avg_quality_score": round(float(row.avg_quality), 1) if row.avg_quality else 0,
        "assessment_count": row.assessment_count,
    } for row in quality_q.all()}

    # Per-location service time, revenue, and booking counts
    bookings_q = await db.execute(
        select(
            Booking.location_id,
            func.count(Booking.id).label("total_bookings"),
            func.sum(
                case(
                    (Booking.status == BookingStatus.COMPLETED, Booking.final_price),
                    else_=0,
                )
            ).label("total_revenue"),
            func.sum(
                case(
                    (Booking.status == BookingStatus.COMPLETED, 1),
                    else_=0,
                )
            ).label("completed_count"),
        )
        .where(*booking_filters)
        .group_by(Booking.location_id)
    )
    bookings_by_location = {}
    for row in bookings_q.all():
        completed = row.completed_count or 0
        bookings_by_location[row.location_id] = {
            "total_bookings": row.total_bookings or 0,
            "completed_count": completed,
            "total_revenue": float(row.total_revenue or 0),
            "revenue_per_service": round(float(row.total_revenue or 0) / completed, 2) if completed > 0 else 0,
        }

    # Per-location complaint rate
    complaints_q = await db.execute(
        select(
            CustomerFeedback.location_id,
            func.count(CustomerFeedback.id).label("complaint_count"),
        )
        .where(
            CustomerFeedback.created_at >= thirty_days_ago,
            CustomerFeedback.overall_rating <= 2,  # Low ratings as proxy for complaints
        )
        .group_by(CustomerFeedback.location_id)
    )
    complaints_by_location = {row.location_id: row.complaint_count for row in complaints_q.all()}

    # Per-location rebooking rate (customers who booked again within 30 days)
    rebooking_q = await db.execute(
        select(
            Booking.location_id,
            func.count(func.distinct(Booking.customer_id)).label("unique_customers"),
        )
        .where(
            Booking.created_at >= thirty_days_ago,
            Booking.status == BookingStatus.COMPLETED,
        )
        .group_by(Booking.location_id)
    )
    customers_by_location = {row.location_id: row.unique_customers for row in rebooking_q.all()}

    # Fetch all active locations
    locations_q = await db.execute(
        select(Location.id, Location.name, Location.code).where(Location.is_active == True)
    )
    locations = locations_q.all()

    # Build benchmark table
    benchmarks = []
    for loc in locations:
        quality_data = quality_by_location.get(loc.id, {})
        booking_data = bookings_by_location.get(loc.id, {})
        complaint_count = complaints_by_location.get(loc.id, 0)
        total_bookings = booking_data.get("total_bookings", 0)

        benchmarks.append({
            "location_id": loc.id,
            "location_name": loc.name,
            "location_code": loc.code,
            "avg_quality_score": quality_data.get("avg_quality_score", 0),
            "assessment_count": quality_data.get("assessment_count", 0),
            "total_bookings": total_bookings,
            "completed_bookings": booking_data.get("completed_count", 0),
            "total_revenue": booking_data.get("total_revenue", 0),
            "revenue_per_service": booking_data.get("revenue_per_service", 0),
            "complaint_count": complaint_count,
            "complaint_rate": round((complaint_count / total_bookings) * 100, 1) if total_bookings > 0 else 0,
            "unique_customers": customers_by_location.get(loc.id, 0),
        })

    # Sort and identify top/bottom performers
    if benchmarks:
        by_quality = sorted(benchmarks, key=lambda x: x["avg_quality_score"], reverse=True)
        top_performer = by_quality[0]["location_name"] if by_quality else None
        bottom_performer = by_quality[-1]["location_name"] if len(by_quality) > 1 else None
    else:
        top_performer = None
        bottom_performer = None

    return APIResponse(
        success=True,
        data={
            "period": "last_30_days",
            "service_id": service_id,
            "locations_count": len(benchmarks),
            "top_performer": top_performer,
            "underperformer": bottom_performer,
            "benchmarks": benchmarks,
        },
    )


register_agent(AgentAction(
    name="cross_branch_benchmark",
    description="Cross-branch benchmarking: quality, timing, complaints, rebooking, revenue per location",
    track="standardization",
    feature="analytics",
    method="get",
    path="/agents/track1/analytics/benchmark",
    handler=cross_branch_benchmark_handler,
    roles=["regional_manager", "franchise_owner", "super_admin"],
    ps_codes=["PS-01.10"],
    requires_ai=False,
))
