"""Sessions router — CRUD for live service sessions (SOP-guided delivery)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, timezone

from app.database import get_db, enum_val
from app.dependencies import get_current_user, require_role
from app.models import ServiceSession, SessionStatus
from app.schemas.common import APIResponse

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post("/", response_model=APIResponse)
async def create_session(
    booking_id: UUID, sop_id: UUID = None,
    soulskin_session_id: UUID = None, steps_total: int = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(["salon_manager", "stylist", "super_admin"])),
):
    session = ServiceSession(
        booking_id=str(booking_id),
        sop_id=str(sop_id) if sop_id else None,
        soulskin_session_id=str(soulskin_session_id) if soulskin_session_id else None,
        steps_total=steps_total,
        status=SessionStatus.NOT_STARTED,
        current_step=1,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return APIResponse(success=True, data={"id": str(session.id)}, message="Session created")


@router.get("/{booking_id}", response_model=APIResponse)
async def get_session(booking_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(
        select(ServiceSession).where(ServiceSession.booking_id == str(booking_id))
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Session not found")
    return APIResponse(success=True, data={
        "id": str(session.id), "booking_id": session.booking_id,
        "sop_id": session.sop_id,
        "status": enum_val(session.status) if session.status else None,
        "current_step": session.current_step,
        "steps_total": session.steps_total,
        "steps_completed": session.steps_completed,
        "started_at": str(session.started_at) if session.started_at else None,
        "completed_at": str(session.completed_at) if session.completed_at else None,
        "products_used": session.products_used,
        "chemical_ratios_used": session.chemical_ratios_used,
        "deviations": session.deviations,
        "ai_coaching_prompts": session.ai_coaching_prompts,
        "soulskin_active": session.soulskin_active,
        "archetype_applied": session.archetype_applied,
        "before_image_url": session.before_image_url,
        "after_image_url": session.after_image_url,
        "quality_score": float(session.quality_score) if session.quality_score else None,
        "sop_compliance_pct": float(session.sop_compliance_pct) if session.sop_compliance_pct else None,
        "stylist_notes": session.stylist_notes,
        "has_offline_changes": session.has_offline_changes,
    })


@router.post("/{booking_id}/start", response_model=APIResponse)
async def start_session(booking_id: UUID, db: AsyncSession = Depends(get_db),
                        user=Depends(require_role(["stylist", "salon_manager"]))):
    result = await db.execute(
        select(ServiceSession).where(ServiceSession.booking_id == str(booking_id))
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Session not found")
    session.status = SessionStatus.ACTIVE
    session.started_at = datetime.now(timezone.utc)
    await db.commit()
    return APIResponse(success=True, message="Session started")


@router.post("/{booking_id}/step/{step_number}", response_model=APIResponse)
async def complete_step(booking_id: UUID, step_number: int,
                        db: AsyncSession = Depends(get_db),
                        user=Depends(require_role(["stylist", "salon_manager"]))):
    result = await db.execute(
        select(ServiceSession).where(ServiceSession.booking_id == str(booking_id))
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Session not found")
    completed = session.steps_completed or []
    if step_number not in completed:
        completed.append(step_number)
    session.steps_completed = completed
    session.current_step = step_number + 1
    if session.status == SessionStatus.NOT_STARTED:
        session.status = SessionStatus.ACTIVE
        session.started_at = datetime.now(timezone.utc)
    await db.commit()
    return APIResponse(success=True, message=f"Step {step_number} completed")


@router.post("/{booking_id}/deviation", response_model=APIResponse)
async def log_deviation(booking_id: UUID, step: int, reason: str,
                        db: AsyncSession = Depends(get_db),
                        user=Depends(require_role(["stylist", "salon_manager"]))):
    result = await db.execute(
        select(ServiceSession).where(ServiceSession.booking_id == str(booking_id))
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Session not found")
    deviations = session.deviations or []
    deviations.append({"step": step, "reason": reason, "logged_at": datetime.now(timezone.utc).isoformat()})
    session.deviations = deviations
    await db.commit()
    return APIResponse(success=True, message="Deviation logged")


@router.post("/{booking_id}/pause", response_model=APIResponse)
async def pause_session(booking_id: UUID, db: AsyncSession = Depends(get_db),
                        user=Depends(require_role(["stylist", "salon_manager"]))):
    result = await db.execute(
        select(ServiceSession).where(ServiceSession.booking_id == str(booking_id))
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Session not found")
    session.status = SessionStatus.PAUSED
    session.paused_at = datetime.now(timezone.utc)
    await db.commit()
    return APIResponse(success=True, message="Session paused")


@router.post("/{booking_id}/resume", response_model=APIResponse)
async def resume_session(booking_id: UUID, db: AsyncSession = Depends(get_db),
                         user=Depends(require_role(["stylist", "salon_manager"]))):
    result = await db.execute(
        select(ServiceSession).where(ServiceSession.booking_id == str(booking_id))
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Session not found")
    session.status = SessionStatus.ACTIVE
    session.resumed_at = datetime.now(timezone.utc)
    await db.commit()
    return APIResponse(success=True, message="Session resumed")


@router.post("/{booking_id}/complete", response_model=APIResponse)
async def complete_session(booking_id: UUID, stylist_notes: str = None,
                           db: AsyncSession = Depends(get_db),
                           user=Depends(require_role(["stylist", "salon_manager"]))):
    result = await db.execute(
        select(ServiceSession).where(ServiceSession.booking_id == str(booking_id))
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Session not found")
    session.status = SessionStatus.COMPLETED
    session.completed_at = datetime.now(timezone.utc)
    if stylist_notes:
        session.stylist_notes = stylist_notes

    # Calculate quality scores
    total = session.steps_total or 1
    completed = len(session.steps_completed or [])
    deviations = len(session.deviations or [])
    session.sop_compliance_pct = round((completed - deviations) / total * 100, 2) if total > 0 else 100

    await db.commit()
    return APIResponse(success=True, message="Session completed")


@router.get("/{booking_id}/guidance", response_model=APIResponse)
async def get_session_guidance(booking_id: UUID, db: AsyncSession = Depends(get_db),
                               user=Depends(get_current_user)):
    """Get AI coaching guidance for current session step."""
    result = await db.execute(
        select(ServiceSession).where(ServiceSession.booking_id == str(booking_id))
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Session not found")

    # Build guidance based on current step and session state
    step = session.current_step or 1
    total = session.steps_total or 1
    deviations = len(session.deviations or [])
    coaching = session.ai_coaching_prompts or {}

    guidance = {
        "current_step": step,
        "total_steps": total,
        "progress_pct": round(step / total * 100, 1) if total > 0 else 0,
        "deviations_logged": deviations,
        "coaching_tip": coaching.get(f"step_{step}",
            "Follow the SOP steps carefully. Take your time with each step."),
        "archetype_active": session.archetype_applied,
        "soulskin_script": None,
    }

    # If SOULSKIN is active, get stylist script
    if session.soulskin_active and session.soulskin_session_id:
        from app.models.soulskin import SoulskinSession
        ss_result = await db.execute(
            select(SoulskinSession).where(SoulskinSession.id == session.soulskin_session_id)
        )
        ss = ss_result.scalar_one_or_none()
        if ss and ss.stylist_script:
            phase = "opening" if step <= total // 3 else "mid_service" if step <= 2 * total // 3 else "closing"
            guidance["soulskin_script"] = ss.stylist_script.get(phase, "")

    return APIResponse(success=True, data=guidance)


@router.post("/{booking_id}/photos", response_model=APIResponse)
async def upload_session_photos(booking_id: UUID, data: dict = None,
                                db: AsyncSession = Depends(get_db),
                                user=Depends(require_role(["stylist", "salon_manager"]))):
    """Upload before/after photos for a session."""
    result = await db.execute(
        select(ServiceSession).where(ServiceSession.booking_id == str(booking_id))
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Session not found")

    photo_data = data or {}
    if "before_image_url" in photo_data:
        session.before_image_url = photo_data["before_image_url"]
    if "after_image_url" in photo_data:
        session.after_image_url = photo_data["after_image_url"]

    await db.commit()
    return APIResponse(success=True, message="Photos uploaded")


@router.get("/{booking_id}/timer", response_model=APIResponse)
async def get_session_timer(booking_id: UUID, db: AsyncSession = Depends(get_db),
                            user=Depends(get_current_user)):
    """Get elapsed and remaining time for a session."""
    result = await db.execute(
        select(ServiceSession).where(ServiceSession.booking_id == str(booking_id))
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Session not found")

    # Get service duration from booking in a single joined query
    expected_mins = 60  # default
    if session.booking_id:
        from app.models.booking import Booking
        from app.models.service import Service
        timer_q = (
            select(Service.duration_minutes)
            .join(Booking, Booking.service_id == Service.id)
            .where(Booking.id == session.booking_id)
        )
        dur_result = (await db.execute(timer_q)).scalar_one_or_none()
        if dur_result:
            expected_mins = dur_result or 60

    elapsed_mins = 0
    remaining_mins = expected_mins
    if session.started_at:
        started = session.started_at
        if started.tzinfo is None:
            from datetime import timezone as tz
            started = started.replace(tzinfo=tz.utc)
        elapsed_secs = (datetime.now(timezone.utc) - started).total_seconds()
        elapsed_mins = round(elapsed_secs / 60, 1)
        remaining_mins = max(0, expected_mins - elapsed_mins)

    status_val = enum_val(session.status) if session.status else None
    is_overtime = elapsed_mins > expected_mins

    return APIResponse(success=True, data={
        "status": status_val,
        "expected_duration_mins": expected_mins,
        "elapsed_mins": elapsed_mins,
        "remaining_mins": remaining_mins,
        "is_overtime": is_overtime,
        "started_at": str(session.started_at) if session.started_at else None,
    })


@router.post("/{booking_id}/sync", response_model=APIResponse)
async def sync_offline_actions(booking_id: UUID, actions: list = None,
                               db: AsyncSession = Depends(get_db),
                               user=Depends(require_role(["stylist", "salon_manager"]))):
    result = await db.execute(
        select(ServiceSession).where(ServiceSession.booking_id == str(booking_id))
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Session not found")
    if actions:
        for action in actions:
            action_type = action.get("type")
            if action_type == "step_completion":
                step = action.get("step_number")
                completed = session.steps_completed or []
                if step and step not in completed:
                    completed.append(step)
                session.steps_completed = completed
            elif action_type == "deviation":
                devs = session.deviations or []
                devs.append({"step": action.get("step"), "reason": action.get("reason"),
                             "logged_at": action.get("logged_at")})
                session.deviations = devs
    session.has_offline_changes = False
    session.last_synced_at = datetime.now(timezone.utc)
    await db.commit()
    return APIResponse(success=True, message="Offline actions synced")
