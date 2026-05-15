"""Mood detection router."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, timezone

from db.db import get_db
from utils.dependencies import get_current_user, require_role
from models import MoodDetection
from schemas.common import APIResponse

router = APIRouter(prefix="/mood", tags=["Mood Detection"])

_EMOTION_KEYWORDS: dict[str, list[str]] = {
    "happy":    ["happy", "great", "wonderful", "amazing", "excited", "love", "joy", "cheerful", "delighted", "fantastic", "smile", "laugh"],
    "anxious":  ["anxious", "nervous", "worried", "scared", "afraid", "stress", "tense", "panic", "fear", "uncertain"],
    "sad":      ["sad", "upset", "cry", "crying", "unhappy", "depressed", "down", "low", "miserable", "heartbroken"],
    "angry":    ["angry", "mad", "frustrated", "irritated", "annoyed", "furious", "rage", "hate"],
    "tired":    ["tired", "exhausted", "sleepy", "fatigue", "drained", "weak", "lethargic"],
    "calm":     ["calm", "relaxed", "peaceful", "serene", "okay", "fine", "good", "stable"],
    "neutral":  [],
}

_ARCHETYPE_MAP: dict[str, str] = {
    "happy": "phoenix",
    "anxious": "moon",
    "sad": "moon",
    "angry": "storm",
    "tired": "river",
    "calm": "bloom",
    "neutral": "bloom",
}

_ENERGY_MAP: dict[str, str] = {
    "happy": "high",
    "anxious": "medium",
    "sad": "low",
    "angry": "high",
    "tired": "low",
    "calm": "medium",
    "neutral": "medium",
}


def _analyze_text_sentiment(text: str) -> tuple[str, float, str]:
    """Return (emotion, confidence, energy_level) from keyword matching."""
    lower = text.lower()
    scores: dict[str, int] = {e: 0 for e in _EMOTION_KEYWORDS}
    for emotion, keywords in _EMOTION_KEYWORDS.items():
        scores[emotion] = sum(1 for kw in keywords if kw in lower)

    best = max(scores, key=lambda e: scores[e])
    total_hits = sum(scores.values())
    if total_hits == 0 or scores[best] == 0:
        return "neutral", 0.5, "medium"

    confidence = min(0.55 + scores[best] * 0.1, 0.90)
    return best, round(confidence, 2), _ENERGY_MAP[best]


@router.get("/", response_model=APIResponse)
async def list_mood_detections(customer_id: UUID = None,
                               db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    q = select(MoodDetection).order_by(MoodDetection.created_at.desc()).limit(20)
    if customer_id:
        q = q.where(MoodDetection.customer_id == customer_id)
    result = await db.execute(q)
    entries = result.scalars().all()
    return APIResponse(success=True, data=[{
        "id": str(m.id), "customer_id": m.customer_id,
        "booking_id": m.booking_id,
        "detected_emotion": m.detected_emotion,
        "emotion_confidence": float(m.emotion_confidence) if m.emotion_confidence else None,
        "secondary_emotion": m.secondary_emotion,
        "energy_level": m.energy_level,
        "stress_indicators": m.stress_indicators,
        "recommended_archetype": m.recommended_archetype,
        "service_adjustment": m.service_adjustment,
        "do_not_recommend": m.do_not_recommend,
        "consent_given": m.consent_given,
        "captured_at": str(m.captured_at) if m.captured_at else None,
    } for m in entries])


@router.post("/", response_model=APIResponse)
async def create_mood_detection(
    customer_id: UUID, booking_id: UUID = None,
    detected_emotion: str = "neutral", emotion_confidence: float = 0.8,
    secondary_emotion: str = None, energy_level: str = "medium",
    recommended_archetype: str = None, service_adjustment: str = None,
    stylist_notes: str = None,
    consent_given: bool = False,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(["stylist", "salon_manager", "super_admin"])),
):
    # If stylist provided freetext notes but didn't specify an emotion, infer it
    if stylist_notes and detected_emotion == "neutral":
        inferred_emotion, inferred_confidence, inferred_energy = _analyze_text_sentiment(stylist_notes)
        if inferred_emotion != "neutral":
            detected_emotion = inferred_emotion
            emotion_confidence = inferred_confidence
            energy_level = inferred_energy

    if not recommended_archetype:
        recommended_archetype = _ARCHETYPE_MAP.get(detected_emotion, "bloom")

    mood = MoodDetection(
        customer_id=str(customer_id),
        booking_id=str(booking_id) if booking_id else None,
        detected_emotion=detected_emotion,
        emotion_confidence=emotion_confidence,
        secondary_emotion=secondary_emotion,
        energy_level=energy_level,
        recommended_archetype=recommended_archetype,
        service_adjustment=service_adjustment,
        consent_given=consent_given,
        captured_at=datetime.now(timezone.utc),
    )
    db.add(mood)
    await db.commit()
    await db.refresh(mood)
    return APIResponse(
        success=True,
        data={"id": str(mood.id), "detected_emotion": detected_emotion, "recommended_archetype": recommended_archetype},
        message="Mood detection recorded",
    )


@router.post("/analyze-text", response_model=APIResponse)
async def analyze_text_mood(
    text: str,
    user=Depends(get_current_user),
):
    """Quick keyword-based mood analysis from free text (no AI needed)."""
    emotion, confidence, energy = _analyze_text_sentiment(text)
    return APIResponse(
        success=True,
        data={
            "detected_emotion": emotion,
            "confidence": confidence,
            "energy_level": energy,
            "recommended_archetype": _ARCHETYPE_MAP.get(emotion, "bloom"),
        },
    )


@router.get("/history/{customer_id}", response_model=APIResponse)
async def mood_history(customer_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(
        select(MoodDetection).where(MoodDetection.customer_id == str(customer_id))
        .order_by(MoodDetection.created_at.desc()).limit(50)
    )
    entries = result.scalars().all()
    return APIResponse(success=True, data=[{
        "id": str(m.id), "detected_emotion": m.detected_emotion,
        "energy_level": m.energy_level,
        "recommended_archetype": m.recommended_archetype,
        "captured_at": str(m.captured_at) if m.captured_at else None,
    } for m in entries])
