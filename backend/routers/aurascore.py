"""AuraScore Router — Idea 16: Real-Time Service Quality Scoring.

Domain logic:
  AuraScore (0–100) = weighted composite of 5 signals:
    1. Customer rating (40%)     — direct post-service star rating
    2. SOP compliance (25%)      — steps completed / total steps
    3. Time compliance (15%)     — penalise if >25% faster or >50% slower than SOP benchmark
    4. Rebook rate (10%)         — did this customer return within 90 days?
    5. Complaint penalty (-10/each) — any complaint raised within 48h of service

  Visibility:
    - Stylist sees own score (personal dashboard)
    - Manager sees branch aggregate + individual stylists
    - Corporate/Admin sees all-branch leaderboard

  Anomaly detection:
    - Weekly Celery task compares this week vs last week per stylist
    - Drop ≥ 15 points → alert stylist + manager + regional manager via WhatsApp/push
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_db, generate_uuid, enum_val
from utils.dependencies import get_current_user, require_role
from models.user import User, UserRole
from schemas.common import APIResponse

router = APIRouter(prefix="/aurascore", tags=["AuraScore — Quality Scoring"])


# ─────────────────────────────────────────────
# Domain: Weighted Score Calculation
# ─────────────────────────────────────────────

WEIGHTS = {
    "customer_rating": 0.40,
    "sop_compliance":  0.25,
    "time_compliance": 0.15,
    "rebook_rate":     0.10,
    "complaint_penalty": 0.10,
}

def calculate_aura_score(
    customer_rating: Optional[float],       # 1.0 – 5.0
    sop_compliance_pct: Optional[float],    # 0 – 100
    actual_duration_mins: Optional[int],
    expected_duration_mins: Optional[int],
    rebook_within_90_days: bool,
    complaint_count: int,
) -> dict:
    """Core AuraScore business logic.

    Returns score (0–100), grade, component breakdown, and plain-English narrative hint.
    """
    components = {}

    # 1. Customer rating → normalise to 0–100
    rating_score = ((customer_rating - 1) / 4) * 100 if customer_rating else 50.0
    components["customer_rating"] = round(rating_score, 1)

    # 2. SOP compliance (already 0–100)
    sop_score = sop_compliance_pct if sop_compliance_pct is not None else 70.0
    components["sop_compliance"] = round(sop_score, 1)

    # 3. Time compliance
    # Ideal: within ±10% of expected. Penalty ramps outside that window.
    if actual_duration_mins and expected_duration_mins and expected_duration_mins > 0:
        ratio = actual_duration_mins / expected_duration_mins
        if 0.90 <= ratio <= 1.10:
            time_score = 100.0
        elif ratio < 0.90:
            # Too fast → possible cutting corners
            shortfall = (0.90 - ratio) / 0.90
            time_score = max(0, 100 - shortfall * 150)
        else:
            # Too slow → service delay
            overrun = (ratio - 1.10) / 0.50
            time_score = max(0, 100 - overrun * 80)
    else:
        time_score = 75.0  # neutral when no data
    components["time_compliance"] = round(time_score, 1)

    # 4. Rebook rate
    rebook_score = 100.0 if rebook_within_90_days else 0.0
    components["rebook_rate"] = rebook_score

    # 5. Complaint penalty
    complaint_penalty = min(complaint_count * 25, 100)   # -25 per complaint, max -100
    components["complaint_penalty_raw"] = complaint_penalty

    # Weighted composite (before penalty)
    raw_score = (
        components["customer_rating"] * WEIGHTS["customer_rating"] +
        components["sop_compliance"]  * WEIGHTS["sop_compliance"]  +
        components["time_compliance"] * WEIGHTS["time_compliance"]  +
        components["rebook_rate"]     * WEIGHTS["rebook_rate"]
    ) / (1 - WEIGHTS["complaint_penalty"])

    # Apply complaint deduction
    final_score = max(0.0, raw_score - complaint_penalty * WEIGHTS["complaint_penalty"])
    final_score = round(min(100.0, final_score), 1)

    # Grade mapping
    if final_score >= 90:
        grade, colour = "S", "#22c55e"
    elif final_score >= 80:
        grade, colour = "A", "#84cc16"
    elif final_score >= 70:
        grade, colour = "B", "#eab308"
    elif final_score >= 55:
        grade, colour = "C", "#f97316"
    else:
        grade, colour = "D", "#ef4444"

    # Identify weakest signal for plain-English coaching hint
    signal_scores = {
        "Customer Rating": rating_score,
        "SOP Compliance": sop_score,
        "Time Management": time_score,
        "Client Rebooking": rebook_score,
    }
    weakest = min(signal_scores, key=signal_scores.get)
    weakest_score = signal_scores[weakest]

    COACHING_HINTS = {
        "Customer Rating": "Focus on the client experience — check in mid-service and ensure comfort.",
        "SOP Compliance": "Review the step-by-step SOP before the service and follow each step.",
        "Time Management": (
            "Service completed too fast — ensure all SOP steps are completed."
            if time_score < 70 and actual_duration_mins and expected_duration_mins and actual_duration_mins < expected_duration_mins
            else "Service is running long — review time benchmarks for this service."
        ),
        "Client Rebooking": "Proactively suggest a next appointment date before the client leaves.",
    }

    return {
        "score": final_score,
        "grade": grade,
        "colour": colour,
        "components": components,
        "weakest_signal": weakest,
        "coaching_hint": COACHING_HINTS.get(weakest, "Keep up the good work!"),
        "complaints": complaint_count,
    }


# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────

class ScoreInput(BaseModel):
    session_id: str
    customer_rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    sop_compliance_pct: Optional[float] = Field(None, ge=0, le=100)
    actual_duration_mins: Optional[int] = None
    expected_duration_mins: Optional[int] = None
    complaint_count: int = 0


@router.post("/calculate", response_model=APIResponse)
async def calculate_and_store_score(
    data: ScoreInput,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Calculate AuraScore for a completed session and persist it.
    Called automatically when a session is marked COMPLETED.
    Also callable by manager to re-score with updated inputs.
    """
    from models.session import ServiceSession
    from models.quality import QualityAssessment
    from models.booking import Booking

    session = await db.get(ServiceSession, data.session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    # Check if customer rebooked within 90 days (lagging quality signal)
    rebook_within_90 = False
    booking = await db.get(Booking, session.booking_id) if session.booking_id else None
    if booking:
        cutoff = (booking.actual_end_at or booking.scheduled_at) + timedelta(days=90) \
            if (booking.actual_end_at or booking.scheduled_at) else None
        if cutoff:
            rebooking_result = await db.execute(
                select(Booking).where(
                    Booking.customer_id == booking.customer_id,
                    Booking.scheduled_at > (booking.actual_end_at or booking.scheduled_at),
                    Booking.scheduled_at <= cutoff,
                )
            )
            rebook_within_90 = rebooking_result.scalar_one_or_none() is not None

    score_data = calculate_aura_score(
        customer_rating=data.customer_rating,
        sop_compliance_pct=data.sop_compliance_pct,
        actual_duration_mins=data.actual_duration_mins,
        expected_duration_mins=data.expected_duration_mins,
        rebook_within_90_days=rebook_within_90,
        complaint_count=data.complaint_count,
    )

    # Persist to QualityAssessment
    qa_result = await db.execute(
        select(QualityAssessment).where(QualityAssessment.session_id == data.session_id)
    )
    qa = qa_result.scalar_one_or_none()
    if not qa:
        qa = QualityAssessment(
            id=generate_uuid(),
            session_id=data.session_id,
            booking_id=session.booking_id,
            stylist_id=session.stylist_id if hasattr(session, 'stylist_id') else None,
        )
        db.add(qa)

    qa.overall_score = score_data["score"]
    qa.sop_compliance_score = score_data["components"]["sop_compliance"]
    qa.timing_score = score_data["components"]["time_compliance"]
    qa.customer_rating = data.customer_rating
    qa.ai_feedback = score_data["coaching_hint"]
    qa.ai_feedback_generated_at = datetime.now(timezone.utc)
    qa.ai_analysis_result = score_data

    # Flag for manager review if score < 55 (grade D)
    if score_data["score"] < 55:
        qa.is_flagged = True
        qa.flag_reason = f"AuraScore {score_data['score']} — grade {score_data['grade']} — {score_data['coaching_hint']}"

    # Update session quality score
    session.quality_score = score_data["score"]
    session.sop_compliance_pct = score_data["components"]["sop_compliance"]

    await db.commit()

    # Trigger anomaly check if flagged
    if qa.is_flagged and qa.stylist_id:
        from tasks.aurascore_tasks import check_stylist_score_drop
        check_stylist_score_drop.delay(qa.stylist_id)

    return APIResponse(
        success=True,
        message="AuraScore calculated",
        data={**score_data, "session_id": data.session_id, "flagged": qa.is_flagged},
    )


@router.get("/stylist/{stylist_id}", response_model=APIResponse)
async def stylist_score_history(
    stylist_id: str,
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Stylist's own score history and trend. Visible to stylist (self), manager, admin."""
    from models.quality import QualityAssessment

    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(QualityAssessment).where(
            QualityAssessment.stylist_id == stylist_id,
            QualityAssessment.created_at >= since,
            QualityAssessment.overall_score.isnot(None),
        ).order_by(QualityAssessment.created_at.desc())
    )
    assessments = result.scalars().all()

    if not assessments:
        return APIResponse(success=True, message="No score data yet", data={"scores": [], "avg": None})

    scores = [a.overall_score for a in assessments if a.overall_score]
    avg = round(sum(scores) / len(scores), 1) if scores else None
    trend = "improving" if len(scores) >= 2 and scores[0] > scores[-1] else \
            "declining" if len(scores) >= 2 and scores[0] < scores[-1] else "stable"

    return APIResponse(
        success=True,
        message="Stylist score history",
        data={
            "stylist_id": stylist_id,
            "avg_score": avg,
            "trend": trend,
            "total_sessions_scored": len(scores),
            "scores": [
                {
                    "date": str(a.created_at)[:10],
                    "score": a.overall_score,
                    "grade": next((g for s, g in [(90,"S"),(80,"A"),(70,"B"),(55,"C")] if (a.overall_score or 0) >= s), "D"),
                    "coaching_hint": a.ai_feedback,
                    "is_flagged": a.is_flagged,
                }
                for a in assessments
            ],
        },
    )


@router.get("/branch/{location_id}", response_model=APIResponse)
async def branch_score_dashboard(
    location_id: str,
    days: int = Query(30, ge=7, le=90),
    current_user: User = Depends(require_role([
        UserRole.SALON_MANAGER, UserRole.FRANCHISE_OWNER,
        UserRole.REGIONAL_MANAGER, UserRole.SUPER_ADMIN
    ])),
    db: AsyncSession = Depends(get_db),
):
    """Branch-level AuraScore dashboard: per-stylist breakdown + branch average.
    Used by manager on their daily dashboard.
    """
    from models.quality import QualityAssessment
    from models.booking import Booking
    from models.staff import StaffProfile
    from models.user import User as UserModel

    since = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        select(QualityAssessment)
        .join(Booking, QualityAssessment.booking_id == Booking.id)
        .where(
            Booking.location_id == location_id,
            QualityAssessment.created_at >= since,
            QualityAssessment.overall_score.isnot(None),
        )
    )
    assessments = result.scalars().all()

    if not assessments:
        return APIResponse(success=True, message="No score data", data={"branch_avg": None, "stylists": []})

    # Group by stylist
    stylist_map: dict = {}
    for a in assessments:
        sid = a.stylist_id or "unknown"
        if sid not in stylist_map:
            stylist_map[sid] = {"scores": [], "flags": 0, "hints": []}
        stylist_map[sid]["scores"].append(a.overall_score)
        if a.is_flagged:
            stylist_map[sid]["flags"] += 1
        if a.ai_feedback:
            stylist_map[sid]["hints"].append(a.ai_feedback)

    all_scores = [a.overall_score for a in assessments]
    branch_avg = round(sum(all_scores) / len(all_scores), 1)

    stylists = []
    for sid, data in stylist_map.items():
        s_avg = round(sum(data["scores"]) / len(data["scores"]), 1)
        stylists.append({
            "stylist_id": sid,
            "avg_score": s_avg,
            "sessions": len(data["scores"]),
            "flags": data["flags"],
            "top_coaching_hint": data["hints"][0] if data["hints"] else None,
        })
    stylists.sort(key=lambda x: x["avg_score"], reverse=True)

    return APIResponse(
        success=True,
        message="Branch AuraScore dashboard",
        data={
            "location_id": location_id,
            "branch_avg": branch_avg,
            "total_sessions": len(assessments),
            "stylists": stylists,
            "flagged_sessions": sum(1 for a in assessments if a.is_flagged),
        },
    )


@router.get("/network/leaderboard", response_model=APIResponse)
async def network_quality_leaderboard(
    days: int = Query(30, ge=7, le=90),
    limit: int = Query(20, ge=5, le=50),
    current_user: User = Depends(require_role([
        UserRole.FRANCHISE_OWNER, UserRole.REGIONAL_MANAGER, UserRole.SUPER_ADMIN
    ])),
    db: AsyncSession = Depends(get_db),
):
    """All-branch AuraScore leaderboard for corporate/HQ view.
    Top 10 and bottom 10 salons by average quality score.
    """
    from models.quality import QualityAssessment
    from models.booking import Booking
    from models.location import Location

    since = datetime.now(timezone.utc) - timedelta(days=days)

    locations_result = await db.execute(select(Location).where(Location.is_active == True))
    locations = locations_result.scalars().all()

    leaderboard = []
    for loc in locations:
        result = await db.execute(
            select(func.avg(QualityAssessment.overall_score).label("avg"),
                   func.count(QualityAssessment.id).label("cnt"))
            .join(Booking, QualityAssessment.booking_id == Booking.id)
            .where(
                Booking.location_id == loc.id,
                QualityAssessment.created_at >= since,
                QualityAssessment.overall_score.isnot(None),
            )
        )
        row = result.one()
        if row.cnt and row.cnt > 0:
            leaderboard.append({
                "location_id": loc.id,
                "location_name": loc.name,
                "city": getattr(loc, "city", ""),
                "avg_score": round(float(row.avg), 1),
                "sessions_scored": int(row.cnt),
                "lat": getattr(loc, "latitude", None),
                "lng": getattr(loc, "longitude", None),
            })

    leaderboard.sort(key=lambda x: x["avg_score"], reverse=True)
    ranked = [{"rank": i + 1, **e} for i, e in enumerate(leaderboard)]

    return APIResponse(
        success=True,
        message=f"Network quality leaderboard — last {days} days",
        data={
            "total_branches": len(ranked),
            "top_10": ranked[:10],
            "bottom_10": ranked[-10:] if len(ranked) > 10 else [],
            "all": ranked[:limit],
        },
    )
