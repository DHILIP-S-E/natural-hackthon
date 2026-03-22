"""SOULSKIN Engine router — soul reading, archetype, experience design."""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.soulskin import SoulskinSession
from app.dependencies import get_current_user, require_role
from app.schemas.common import APIResponse

router = APIRouter(prefix="/soulskin", tags=["SOULSKIN Engine"])

ARCHETYPES = {
    "phoenix": {"name": "Phoenix", "emoji": "🔥", "color": "#E8611A", "element": "Fire",
                "description": "You are standing at the edge of something ending. You are not afraid of the fire. You are ready to become what you always were."},
    "river": {"name": "River", "emoji": "🌊", "color": "#4A9FD4", "element": "Water",
              "description": "You are in flow. Something is shifting inside you, and you're learning to move with it instead of against it."},
    "moon": {"name": "Moon", "emoji": "🌙", "color": "#7B68C8", "element": "Light",
             "description": "You are in a quiet phase. You need softness, space, and gentle reflection. Your beauty is subtle and deep."},
    "bloom": {"name": "Bloom", "emoji": "🌸", "color": "#E8A87C", "element": "Earth",
              "description": "You are growing. Something new is opening inside you — a celebration, a milestone, a beginning."},
    "storm": {"name": "Storm", "emoji": "⛈️", "color": "#6B8FA6", "element": "Air",
              "description": "You carry weight today. Tension, change, or turbulence. You need grounding, not stimulation."},
}


@router.get("/archetypes", response_model=APIResponse)
async def get_archetypes():
    """List all SOULSKIN archetypes with descriptions."""
    return APIResponse(success=True, data=ARCHETYPES)


@router.post("/sessions", response_model=APIResponse)
async def create_soulskin_session(
    data: dict,
    current_user: User = Depends(require_role(["stylist", "salon_manager", "super_admin"])),
    db: AsyncSession = Depends(get_db),
):
    """Start a new SOULSKIN soul reading session."""
    session = SoulskinSession(
        booking_id=data.get("booking_id"),
        customer_id=data.get("customer_id") or None,
        stylist_id=data.get("stylist_id"),
        location_id=data.get("location_id"),
    )
    db.add(session)
    await db.flush()
    return APIResponse(success=True, data={"id": session.id}, message="SOULSKIN session started")


@router.patch("/sessions/{session_id}", response_model=APIResponse)
async def update_soulskin_session(
    session_id: str,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update SOULSKIN session with customer's answers."""
    result = await db.execute(select(SoulskinSession).where(SoulskinSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    for field in ["question_1_song", "question_2_colour", "question_3_word"]:
        if field in data:
            setattr(session, field, data[field])

    return APIResponse(success=True, message="Answers recorded")


@router.post("/sessions/{session_id}/generate", response_model=APIResponse)
async def generate_soul_reading(
    session_id: str,
    current_user: User = Depends(require_role(["stylist", "salon_manager", "super_admin"])),
    db: AsyncSession = Depends(get_db),
):
    """Generate the full soul reading via LLM (demo mode: returns pre-generated content)."""
    result = await db.execute(select(SoulskinSession).where(SoulskinSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Generate soul reading via AI service (falls back to rule-based if OpenAI unavailable)
    from app.services.ai_service import generate_soul_reading as ai_generate

    # Build customer context for AI
    customer_ctx = {}
    if session.customer_id:
        from app.models.customer import CustomerProfile
        cp_result = await db.execute(select(CustomerProfile).where(CustomerProfile.id == session.customer_id))
        cp = cp_result.scalar_one_or_none()
        if cp:
            customer_ctx = {
                "hair_type": cp.hair_type, "skin_type": cp.skin_type,
                "dominant_archetype": cp.dominant_archetype,
                "hair_damage_level": cp.hair_damage_level,
                "primary_goal": cp.primary_goal,
            }

    ai_result = await ai_generate(
        song=session.question_1_song or "",
        colour=session.question_2_colour or "",
        word=session.question_3_word or "",
        customer_context=customer_ctx,
    )

    archetype = ai_result.get("archetype", "bloom")
    arch_data = ARCHETYPES.get(archetype, ARCHETYPES["bloom"])

    # Assign all generated fields to session
    session.archetype = archetype
    session.soul_reading = ai_result.get("soul_reading", arch_data["description"])
    session.archetype_reason = ai_result.get("archetype_reason", "")
    session.service_protocol = ai_result.get("service_protocol", {})
    session.colour_direction = ai_result.get("colour_direction", {})
    session.sensory_environment = ai_result.get("sensory_environment", {})
    session.touch_protocol = ai_result.get("touch_protocol", {})
    session.custom_formula = ai_result.get("custom_formula", {})
    session.stylist_script = ai_result.get("stylist_script", {})
    session.mirror_monologue = ai_result.get("mirror_monologue", "")
    session.private_life_note = ai_result.get("private_life_note", "")
    session.look_created = ai_result.get("look_created", "")
    session.session_completed = True

    # Push archetype to customer profile (spec §7.2 step 6)
    if session.customer_id:
        from app.models.customer import CustomerProfile
        cp_result2 = await db.execute(select(CustomerProfile).where(CustomerProfile.id == session.customer_id))
        cp2 = cp_result2.scalar_one_or_none()
        if cp2:
            cp2.dominant_archetype = archetype
            history = cp2.archetype_history or []
            history.append({"archetype": archetype, "date": str(date.today()), "session_id": session.id})
            cp2.archetype_history = history

    return APIResponse(
        success=True,
        data={
            "archetype": archetype,
            "archetype_info": arch_data,
            "soul_reading": session.soul_reading,
            "archetype_reason": session.archetype_reason,
            "service_protocol": session.service_protocol,
            "colour_direction": session.colour_direction,
            "sensory_environment": session.sensory_environment,
            "touch_protocol": session.touch_protocol,
            "custom_formula": session.custom_formula,
            "stylist_script": session.stylist_script,
            "mirror_monologue": session.mirror_monologue,
        },
        message="Soul reading generated",
    )


@router.get("/sessions/{session_id}", response_model=APIResponse)
async def get_soulskin_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get full SOULSKIN session data."""
    result = await db.execute(select(SoulskinSession).where(SoulskinSession.id == session_id))
    s = result.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")

    return APIResponse(success=True, data={
        "id": s.id, "booking_id": s.booking_id, "customer_id": s.customer_id,
        "question_1_song": s.question_1_song, "question_2_colour": s.question_2_colour,
        "question_3_word": s.question_3_word, "archetype": s.archetype,
        "soul_reading": s.soul_reading, "archetype_reason": s.archetype_reason,
        "service_protocol": s.service_protocol, "colour_direction": s.colour_direction,
        "sensory_environment": s.sensory_environment, "touch_protocol": s.touch_protocol,
        "custom_formula": s.custom_formula, "stylist_script": s.stylist_script,
        "mirror_monologue": s.mirror_monologue, "private_life_note": s.private_life_note,
        "look_created": s.look_created, "session_completed": s.session_completed,
    })


@router.get("/journal/{customer_id}", response_model=APIResponse)
async def get_soul_journal(
    customer_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all SOULSKIN journal entries for a customer."""
    result = await db.execute(
        select(SoulskinSession)
        .where(SoulskinSession.customer_id == customer_id, SoulskinSession.session_completed == True)
        .order_by(SoulskinSession.created_at.desc())
    )
    sessions = result.scalars().all()

    return APIResponse(success=True, data=[
        {
            "id": s.id, "archetype": s.archetype,
            "soul_reading": s.soul_reading, "private_life_note": s.private_life_note,
            "look_created": s.look_created, "question_2_colour": s.question_2_colour,
            "question_3_word": s.question_3_word,
            "created_at": str(s.created_at) if s.created_at else None,
        }
        for s in sessions
    ])
