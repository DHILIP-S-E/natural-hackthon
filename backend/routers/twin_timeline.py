"""Digital Beauty Twin — Idea 22: Photo Timeline + Health Score + AI Narrative.

Domain logic:
  Health Score (0–100) = weighted average of:
    - Skin smoothness trend    (30%)
    - Hair vitality trend      (25%)
    - Hydration index trend    (20%)
    - Consistency score        (15%) — how regularly customer comes in
    - Progression score        (10%) — are scores improving over time?

  Photo timeline = series of before/after snapshots linked to service sessions.
  AI Narrative (Gemini): "Your skin has improved 18% since March. Your keratin
  treatment on Apr 12 added significant hair vitality..."
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_db, generate_uuid
from utils.dependencies import get_current_user
from models.user import User
from schemas.common import APIResponse

router = APIRouter(prefix="/twin/timeline", tags=["Digital Beauty Twin — Timeline"])


def _compute_health_score(
    skin_scores: list[float],
    hair_scores: list[float],
    hydration_scores: list[float],
    visit_count: int,
    days_since_start: int,
) -> dict:
    """Compute composite health score 0–100."""
    def trend_score(series: list[float]) -> float:
        if not series:
            return 50.0
        if len(series) == 1:
            return float(series[0])
        # Simple linear regression slope normalised to 0–100
        n = len(series)
        xs = list(range(n))
        mean_x = sum(xs) / n
        mean_y = sum(series) / n
        numer = sum((xs[i] - mean_x) * (series[i] - mean_y) for i in range(n))
        denom = sum((xs[i] - mean_x) ** 2 for i in range(n)) or 1
        slope = numer / denom
        # Positive slope = improving; cap at ±20 pts adjustment
        latest = series[-1]
        return round(min(100, max(0, latest + slope * 3)), 1)

    # Consistency: visits per month; ideal = 2/month
    months = max(1, days_since_start / 30)
    visits_per_month = visit_count / months
    consistency = min(100, (visits_per_month / 2) * 100)

    # Progression: is latest score better than earliest?
    def progression(series: list[float]) -> float:
        if len(series) < 2:
            return 50.0
        delta = series[-1] - series[0]
        return min(100, max(0, 50 + delta))

    skin = trend_score(skin_scores)
    hair = trend_score(hair_scores)
    hydration = trend_score(hydration_scores)
    prog = (
        progression(skin_scores) * 0.4
        + progression(hair_scores) * 0.35
        + progression(hydration_scores) * 0.25
    )

    composite = (
        skin * 0.30
        + hair * 0.25
        + hydration * 0.20
        + consistency * 0.15
        + prog * 0.10
    )
    composite = round(composite, 1)

    grade = (
        "Excellent" if composite >= 85
        else "Good" if composite >= 70
        else "Fair" if composite >= 55
        else "Needs Attention"
    )

    return {
        "health_score": composite,
        "grade": grade,
        "breakdown": {
            "skin_score": skin,
            "hair_score": hair,
            "hydration_score": hydration,
            "consistency_score": round(consistency, 1),
            "progression_score": round(prog, 1),
        },
    }


async def _generate_ai_narrative(
    customer_name: str,
    health_score: float,
    timeline_events: list[dict],
    top_service: str,
) -> str:
    """Generate personalised health journey narrative via Gemini."""
    from utils.secrets import settings
    from services.ai_service import _call_gemini, _call_openai

    events_text = "\n".join(
        f"- {e['date']}: {e['service']} (skin: {e.get('skin_score','?')}, hair: {e.get('hair_score','?')})"
        for e in timeline_events[-6:]
    )
    prompt = (
        f"You are AURA's beauty health analyst. Write a warm, personal 3-sentence narrative "
        f"for {customer_name}'s beauty health journey. "
        f"Overall health score: {health_score}/100. "
        f"Recent sessions:\n{events_text}\n"
        f"Most booked service: {top_service}. "
        f"Mention specific improvements, the impact of key treatments, and one forward-looking tip. "
        f"Tone: encouraging, specific, expert. Max 80 words."
    )
    try:
        if settings.AI_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
            return await _call_gemini(prompt)
        elif settings.OPENAI_API_KEY:
            return await _call_openai(prompt)
    except Exception:
        pass

    # Fallback narrative
    grade = "excellent" if health_score >= 85 else "good" if health_score >= 70 else "steady"
    return (
        f"Your beauty health score is {health_score:.0f}/100 — {grade} progress! "
        f"Your recent {top_service} sessions have been a key driver. "
        f"Keep up your current routine and consider booking a follow-up in 3–4 weeks for continued improvement."
    )


@router.get("/{customer_id}", response_model=APIResponse)
async def get_twin_timeline(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get full Digital Beauty Twin timeline with health score + AI narrative.
    Returns photo milestones, per-session scores, and trend analysis.
    """
    from models import DigitalBeautyTwin
    from models.customer import CustomerProfile
    from models.booking import Booking
    from models.user import User as UserModel

    # Get twin
    twin_result = await db.execute(
        select(DigitalBeautyTwin).where(DigitalBeautyTwin.customer_id == customer_id)
    )
    twin = twin_result.scalar_one_or_none()

    # Get customer profile
    cp_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.id == customer_id)
    )
    cp = cp_result.scalar_one_or_none()
    if not cp:
        raise HTTPException(404, "Customer not found")

    # Get customer name
    user_result = await db.execute(
        select(UserModel).where(UserModel.id == cp.user_id)
    )
    customer_user = user_result.scalar_one_or_none()
    customer_name = customer_user.first_name if customer_user else "Customer"

    # Build timeline from skin_timeline stored in twin
    timeline_events: list[dict] = []
    skin_scores: list[float] = []
    hair_scores: list[float] = []
    hydration_scores: list[float] = []
    service_counts: dict[str, int] = {}

    if twin and twin.skin_timeline:
        raw = twin.skin_timeline if isinstance(twin.skin_timeline, list) else []
        for entry in raw:
            skin_scores.append(float(entry.get("skin_score", 50)))
            hair_scores.append(float(entry.get("hair_score", 50)))
            hydration_scores.append(float(entry.get("hydration_score", 50)))
            svc = entry.get("service", "")
            service_counts[svc] = service_counts.get(svc, 0) + 1
            timeline_events.append({
                "date": entry.get("date", ""),
                "service": svc,
                "photo_url": entry.get("photo_url"),
                "skin_score": entry.get("skin_score"),
                "hair_score": entry.get("hair_score"),
                "hydration_score": entry.get("hydration_score"),
                "notes": entry.get("notes", ""),
            })

    # Calculate days since first visit
    first_visit_date = None
    if cp.created_at:
        first_visit_date = cp.created_at
    days_since_start = (datetime.now(timezone.utc) - first_visit_date).days if first_visit_date else 90

    health = _compute_health_score(
        skin_scores=skin_scores or [50.0],
        hair_scores=hair_scores or [50.0],
        hydration_scores=hydration_scores or [50.0],
        visit_count=cp.total_visits or 1,
        days_since_start=max(1, days_since_start),
    )

    top_service = max(service_counts, key=service_counts.get) if service_counts else "Hair Services"

    narrative = await _generate_ai_narrative(
        customer_name=customer_name,
        health_score=health["health_score"],
        timeline_events=timeline_events,
        top_service=top_service,
    )

    return APIResponse(
        success=True,
        message="Digital Beauty Twin timeline",
        data={
            "customer_id": customer_id,
            "customer_name": customer_name,
            "twin_exists": twin is not None,
            "consent_given": twin.consent_given if twin else False,
            **health,
            "ai_narrative": narrative,
            "timeline": timeline_events,
            "total_sessions_analysed": len(timeline_events),
            "top_service": top_service,
            "last_rebuilt_at": str(twin.last_rebuilt_at) if twin and twin.last_rebuilt_at else None,
        },
    )


@router.post("/{customer_id}/snapshot", response_model=APIResponse)
async def add_timeline_snapshot(
    customer_id: str,
    body: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a new snapshot entry to the Digital Beauty Twin timeline.
    Called by stylists after completing a service session with scores.
    body: { service, skin_score, hair_score, hydration_score, notes, photo_url }
    """
    from models import DigitalBeautyTwin

    twin_result = await db.execute(
        select(DigitalBeautyTwin).where(DigitalBeautyTwin.customer_id == customer_id)
    )
    twin = twin_result.scalar_one_or_none()

    if not twin:
        twin = DigitalBeautyTwin(
            id=generate_uuid(),
            customer_id=customer_id,
            consent_given=True,
            skin_timeline=[],
            is_active=True,
            last_rebuilt_at=datetime.now(timezone.utc),
        )
        db.add(twin)

    timeline = twin.skin_timeline or []
    entry = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "service": body.get("service", ""),
        "skin_score": body.get("skin_score"),
        "hair_score": body.get("hair_score"),
        "hydration_score": body.get("hydration_score"),
        "photo_url": body.get("photo_url"),
        "notes": body.get("notes", ""),
        "recorded_by": str(current_user.id),
    }
    timeline.append(entry)
    twin.skin_timeline = timeline
    twin.last_rebuilt_at = datetime.now(timezone.utc)

    await db.commit()

    return APIResponse(
        success=True,
        message="Timeline snapshot added",
        data={"customer_id": customer_id, "entry": entry, "total_entries": len(timeline)},
    )
