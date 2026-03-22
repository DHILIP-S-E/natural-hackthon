"""Mood detection router."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, timezone

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models import MoodDetection
from app.schemas.common import APIResponse

router = APIRouter(prefix="/mood", tags=["Mood Detection"])


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
    consent_given: bool = False,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(["stylist", "salon_manager", "super_admin"])),
):
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
    return APIResponse(success=True, data={"id": str(mood.id)}, message="Mood detection recorded")


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
