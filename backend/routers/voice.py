"""Voice Assistant router — Feature 15: Hands-free AI Stylist Assistant.

Stylist speaks → Web Speech API transcribes in browser → sends text here →
Gemini parses intent → fetches from AURA DB → returns spoken response.
Button-press activation only (never always-on). Multi-language support.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_db
from utils.dependencies import get_current_user
from models.user import User
from schemas.common import APIResponse

router = APIRouter(prefix="/voice", tags=["Voice Assistant"])

SUPPORTED_LANGUAGES = {
    "ta": "Tamil",
    "te": "Telugu",
    "hi": "Hindi",
    "kn": "Kannada",
    "ml": "Malayalam",
    "en": "English",
}

INTENT_SYSTEM_PROMPT = """You are AURA, an AI assistant for salon stylists.
Parse the stylist's spoken query and return ONLY valid JSON:

{
  "intent": "client_history" | "technique_steps" | "staff_availability" | "product_info" | "booking_info" | "general",
  "entities": {
    "client_name": null or "name",
    "service_name": null or "service",
    "stylist_name": null or "name",
    "product_name": null or "name",
    "time_slot": null or "time",
    "booking_id": null or "id"
  },
  "response_language": "en" | "ta" | "te" | "hi" | "kn" | "ml",
  "spoken_query": "original query"
}

Be concise. Only return the JSON."""


class VoiceQuery(BaseModel):
    transcript: str
    stylist_language: str = "en"
    location_id: Optional[str] = None
    active_booking_id: Optional[str] = None


_INTENT_KEYWORDS: list[tuple[str, list[str]]] = [
    ("client_history",    ["client", "customer", "history", "allergy", "allergic", "profile", "last visit", "last time"]),
    ("staff_availability",["available", "free", "busy", "stylist", "who is", "schedule", "slot", "appointment"]),
    ("technique_steps",   ["how to", "technique", "steps", "method", "procedure", "process", "tutorial", "guide"]),
    ("product_info",      ["product", "ingredient", "brand", "chemical", "formula", "ratio", "shampoo", "conditioner"]),
    ("booking_info",      ["booking", "appointment", "reservation", "booked", "when", "time", "today"]),
]


def _rule_based_intent(transcript: str, language: str) -> dict:
    """Keyword-based intent parser used when no AI provider is configured."""
    lower = transcript.lower()
    matched_intent = "general"
    for intent, keywords in _INTENT_KEYWORDS:
        if any(kw in lower for kw in keywords):
            matched_intent = intent
            break

    words = lower.split()
    entities: dict = {}
    # Simple name extraction: word after "client", "customer", "stylist" cue
    for cue, field in [("client", "client_name"), ("customer", "client_name"), ("stylist", "stylist_name")]:
        try:
            idx = words.index(cue)
            if idx + 1 < len(words):
                entities[field] = words[idx + 1].capitalize()
        except ValueError:
            pass

    return {"intent": matched_intent, "entities": entities, "response_language": language, "spoken_query": transcript}


async def _call_ai_for_intent(transcript: str, language: str) -> dict:
    """Parse speech transcript into structured intent using Gemini/OpenAI."""
    import json
    from utils.secrets import settings
    from services.ai_service import _call_gemini, _call_openai

    prompt = f"{INTENT_SYSTEM_PROMPT}\n\nStylist language: {language}\nQuery: {transcript}"

    try:
        if settings.AI_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
            text = await _call_gemini(prompt)
        elif settings.OPENAI_API_KEY:
            text = await _call_openai(prompt)
        else:
            return _rule_based_intent(transcript, language)

        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except Exception:
        return _rule_based_intent(transcript, language)


async def _fetch_client_history(entities: dict, location_id: Optional[str], db: AsyncSession) -> str:
    """Fetch client's last service/product history from Beauty Passport."""
    from models.customer import CustomerProfile
    from models.user import User as UserModel

    name = entities.get("client_name", "")
    if not name:
        return "Please say the client's name."

    result = await db.execute(
        select(UserModel).where(
            UserModel.first_name.ilike(f"%{name}%")
        )
    )
    user = result.scalar_one_or_none()
    if not user:
        return f"No client named {name} found in this salon."

    cp_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.user_id == user.id)
    )
    cp = cp_result.scalar_one_or_none()
    if not cp:
        return f"{name}'s Beauty Passport is not set up yet."

    allergies = ", ".join(cp.known_allergies or []) or "none recorded"
    hair = cp.current_hair_color or "natural"
    skin = cp.skin_type or "not recorded"
    return (
        f"{name}'s profile: Hair colour is {hair}. "
        f"Skin type is {skin}. Known allergies: {allergies}. "
        f"Last visit: {cp.last_visit_date or 'no record'}."
    )


async def _fetch_staff_availability(entities: dict, location_id: Optional[str], db: AsyncSession) -> str:
    """Check if a specific stylist is available at a given time."""
    from models.staff import StaffProfile

    name = entities.get("stylist_name", "")
    time_slot = entities.get("time_slot", "")

    if not name:
        return "Please say the stylist's name."

    from models.user import User as UserModel
    result = await db.execute(
        select(UserModel).where(UserModel.first_name.ilike(f"%{name}%"))
    )
    user = result.scalar_one_or_none()
    if not user:
        return f"No stylist named {name} found."

    staff_result = await db.execute(
        select(StaffProfile).where(StaffProfile.user_id == user.id)
    )
    staff = staff_result.scalar_one_or_none()
    if not staff:
        return f"{name} is not registered as a stylist."

    status = "available" if staff.is_available else "not available right now"
    return f"{name} is {status}. Skill level: {staff.skill_level or 'L1'}. Specialties: {', '.join(staff.specializations or ['general'])}."


@router.post("/query", response_model=APIResponse)
async def process_voice_query(
    query: VoiceQuery,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Process a voice query from the stylist.

    Flow: Transcript from Web Speech API → Intent parsing → DB fetch → Spoken response.
    Privacy: No audio is stored. Only transcript is processed.
    """
    if not query.transcript.strip():
        raise HTTPException(400, "Empty transcript received.")

    lang = query.stylist_language if query.stylist_language in SUPPORTED_LANGUAGES else "en"
    intent_data = await _call_ai_for_intent(query.transcript, lang)
    intent = intent_data.get("intent", "general")
    entities = intent_data.get("entities", {})

    # Route to the correct data fetcher
    if intent == "client_history":
        spoken_response = await _fetch_client_history(entities, query.location_id, db)
    elif intent == "staff_availability":
        spoken_response = await _fetch_staff_availability(entities, query.location_id, db)
    elif intent == "technique_steps":
        service_name = entities.get("service_name", "")
        spoken_response = (
            f"Opening technique guide for {service_name}. "
            "Please check your tablet screen for the step-by-step instructions."
            if service_name else "Please say the service name."
        )
    elif intent == "booking_info":
        spoken_response = "Please check the booking screen on your tablet for appointment details."
    else:
        from utils.secrets import settings
        if settings.GEMINI_API_KEY or settings.OPENAI_API_KEY:
            from services.ai_service import _call_gemini, _call_openai
            context = f"Stylist query (language: {lang}): {query.transcript}\nGive a short helpful response for a salon stylist."
            try:
                if settings.AI_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
                    spoken_response = await _call_gemini(context)
                else:
                    spoken_response = await _call_openai(context)
            except Exception:
                spoken_response = "I couldn't process that. Please try again."
        else:
            spoken_response = "AI assistant is not configured. Please contact your manager."

    return APIResponse(
        success=True,
        message="Voice query processed",
        data={
            "transcript": query.transcript,
            "intent": intent,
            "entities": entities,
            "spoken_response": spoken_response,
            "language": lang,
            "language_name": SUPPORTED_LANGUAGES[lang],
        },
    )


@router.get("/languages", response_model=APIResponse)
async def supported_languages():
    """List supported languages for the voice assistant."""
    return APIResponse(
        success=True,
        message="Supported languages",
        data={"languages": [{"code": k, "name": v} for k, v in SUPPORTED_LANGUAGES.items()]},
    )
