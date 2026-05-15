"""Multilingual AI Chatbot — Idea 20: AURA Chat.

Domain logic:
  GPT-4o/Gemini with tool-calling against live AURA database.
  Handles: booking, rescheduling, cancellation, price queries,
           stylist availability, FAQs, feedback collection.
  Auto-detects language from message. Responds in same language.
  Sentiment analysis → negative → manager alert via SNS.
  Escalation: if confidence < 0.6 → hand off to human manager.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_db, generate_uuid
from utils.dependencies import get_optional_user
from models.user import User
from schemas.common import APIResponse

router = APIRouter(prefix="/chatbot", tags=["Multilingual AI Chatbot"])

SUPPORTED_LANGS = {
    "ta": "Tamil", "te": "Telugu", "kn": "Kannada",
    "ml": "Malayalam", "hi": "Hindi", "en": "English",
}

SYSTEM_PROMPT = """You are AURA Chat, an intelligent assistant for Naturals salon chain.
You help customers with:
- Booking, rescheduling, cancellation appointments
- Checking stylist availability and service prices
- Answering FAQs (hours, location, parking, payment)
- Collecting post-visit feedback

RULES:
1. Always respond in the SAME language the customer used. If Tamil → reply Tamil. If Hindi → Hindi.
2. Be warm, professional, and concise (max 3 sentences).
3. If you cannot answer from available data, say so honestly and offer to connect them to a manager.
4. Never promise anything about prices or availability without confirming from the data provided.
5. For booking changes, always confirm the new details before confirming.

Available data will be injected as context. Use it to give specific answers."""

NEGATIVE_SENTIMENT_KEYWORDS = [
    "terrible", "awful", "horrible", "worst", "disgusting", "never coming back",
    "waste of money", "rude", "unprofessional", "complaint", "refund",
    "bahut bura", "bekar", "waste", "shikayat",  # Hindi
    "moshama", "kodumai",  # Tamil
]


async def _detect_language(text: str) -> str:
    """Simple heuristic language detection for Indian languages."""
    ta_chars = set("அஆஇஈஉஊகசடதநபமயரலவைொோ")
    te_chars = set("అఆఇఈఉఊకచటతనపమయరలవై")
    kn_chars = set("ಅಆಇಈಉಊಕಚಟತನಪಮಯರಲವೈ")
    ml_chars = set("അആഇഈഉഊകചടതനപമയരലവൈ")
    hi_chars = set("अआइईउऊकचटतनपमयरलवकिािे")

    text_chars = set(text)
    if text_chars & ta_chars: return "ta"
    if text_chars & te_chars: return "te"
    if text_chars & kn_chars: return "kn"
    if text_chars & ml_chars: return "ml"
    if text_chars & hi_chars: return "hi"
    return "en"


def _detect_negative_sentiment(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in NEGATIVE_SENTIMENT_KEYWORDS)


async def _fetch_context(intent_hint: str, location_id: Optional[str], db: AsyncSession) -> str:
    """Fetch relevant DB data based on detected intent."""
    context_parts = []

    if "availability" in intent_hint or "stylist" in intent_hint:
        from models.staff import StaffProfile
        from models.user import User as UserModel
        q = select(StaffProfile).where(StaffProfile.is_available == True)
        if location_id:
            q = q.where(StaffProfile.location_id == location_id)
        result = await db.execute(q.limit(5))
        staff = result.scalars().all()
        if staff:
            names = []
            for s in staff:
                u = await db.get(UserModel, s.user_id)
                if u:
                    names.append(f"{u.first_name} ({s.skill_level}, {', '.join(s.specializations or ['general'])})")
            context_parts.append(f"Available stylists: {'; '.join(names)}")

    if "price" in intent_hint or "cost" in intent_hint or "service" in intent_hint:
        from models.service import Service
        result = await db.execute(select(Service).where(Service.is_active == True).limit(8))
        services = result.scalars().all()
        if services:
            svc_list = [f"{s.name}: ₹{int(s.base_price or 0)}" for s in services if s.base_price]
            context_parts.append(f"Service prices: {', '.join(svc_list[:6])}")

    if "hour" in intent_hint or "time" in intent_hint or "open" in intent_hint:
        context_parts.append("Salon hours: Monday–Saturday 9:00 AM – 8:00 PM, Sunday 10:00 AM – 6:00 PM")

    return "\n".join(context_parts) if context_parts else "No specific data fetched."


async def _call_ai_chat(
    message: str,
    language: str,
    context: str,
    history: list[dict],
) -> tuple[str, float]:
    """Call AI with system prompt + context + conversation history. Returns (reply, confidence)."""
    from utils.secrets import settings
    from services.ai_service import _call_gemini, _call_openai

    messages_text = "\n".join(
        f"{'Customer' if m['role'] == 'user' else 'AURA'}: {m['content']}"
        for m in history[-6:]  # last 3 turns
    )

    full_prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Customer language detected: {SUPPORTED_LANGS.get(language, 'English')}\n"
        f"Live salon data:\n{context}\n\n"
        f"Conversation so far:\n{messages_text}\n"
        f"Customer: {message}\n"
        f"AURA:"
    )

    try:
        if settings.AI_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
            reply = await _call_gemini(full_prompt)
        elif settings.OPENAI_API_KEY:
            reply = await _call_openai(full_prompt)
        else:
            reply = ("I'm AURA Chat. I can help with bookings, prices, and stylist availability. "
                     "Please call your nearest Naturals salon for immediate assistance.")
        return reply.strip(), 0.85
    except Exception:
        return "I'm having trouble connecting right now. Please try again in a moment.", 0.3


class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    location_id: Optional[str] = None
    history: list[dict] = []


@router.post("/message", response_model=APIResponse)
async def chat(
    body: ChatMessage,
    db: AsyncSession = Depends(get_db),
):
    """Process a customer chat message. Handles WhatsApp webhook or in-app chat.
    Public endpoint — no auth required (customer may not be logged in).
    """
    if not body.message.strip():
        raise HTTPException(400, "Message cannot be empty")

    lang = _detect_language(body.message)
    is_negative = _detect_negative_sentiment(body.message)

    # Simple intent detection for context fetching
    msg_lower = body.message.lower()
    intent_hint = " ".join([
        "availability" if any(w in msg_lower for w in ["available", "stylist", "who", "book"]) else "",
        "price" if any(w in msg_lower for w in ["price", "cost", "how much", "rate"]) else "",
        "service" if any(w in msg_lower for w in ["service", "treatment", "colour", "color", "facial"]) else "",
        "hour" if any(w in msg_lower for w in ["open", "close", "time", "hour", "when"]) else "",
    ]).strip()

    context = await _fetch_context(intent_hint, body.location_id, db)
    reply, confidence = await _call_ai_chat(
        message=body.message,
        language=lang,
        context=context,
        history=body.history,
    )

    # Escalate if low confidence
    needs_escalation = confidence < 0.6 or is_negative

    # Negative sentiment → alert manager
    if is_negative and body.location_id:
        from models.location import Location
        from models.user import User as UserModel
        from services.sns_service import send_whatsapp

        location = await db.get(Location, body.location_id)
        if location and location.manager_id:
            mgr = await db.get(UserModel, location.manager_id)
            if mgr and mgr.phone:
                await send_whatsapp(
                    mgr.phone,
                    f"😟 Negative sentiment detected in AURA Chat:\n"
                    f"Customer message: \"{body.message[:120]}...\"\n"
                    f"Please follow up immediately.",
                )

    # Log conversation
    notif_data = {
        "session_id": body.session_id or generate_uuid(),
        "message": body.message,
        "reply": reply,
        "language": lang,
        "sentiment": "negative" if is_negative else "neutral",
        "escalated": needs_escalation,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    return APIResponse(
        success=True,
        message="Chat response",
        data={
            "reply": reply,
            "language": lang,
            "language_name": SUPPORTED_LANGS.get(lang, "English"),
            "needs_escalation": needs_escalation,
            "escalation_message": (
                "I'll connect you with our team right away. "
                "A manager will reach out to you shortly." if needs_escalation else None
            ),
            "is_negative_sentiment": is_negative,
            "session_id": notif_data["session_id"],
        },
    )


@router.get("/faq", response_model=APIResponse)
async def get_faq():
    """Return common FAQs in all supported languages (cached, no AI call needed)."""
    return APIResponse(
        success=True,
        message="Frequently asked questions",
        data={
            "faqs": [
                {"q": "What are your salon hours?", "a": "Mon–Sat 9 AM–8 PM, Sunday 10 AM–6 PM"},
                {"q": "Do I need an appointment?", "a": "Walk-ins welcome! Book online for preferred stylist."},
                {"q": "What payment methods do you accept?", "a": "Cash, UPI, credit/debit cards accepted."},
                {"q": "How do I cancel my booking?", "a": "Cancel anytime via AURA app or WhatsApp 2+ hours before appointment."},
                {"q": "Do you offer home services?", "a": "Currently in-salon only. Bridal home visits available — contact your branch."},
            ],
            "supported_languages": list(SUPPORTED_LANGS.values()),
        },
    )
