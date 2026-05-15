"""Eco Tracker router — Feature 14: Sustainable Beauty Intelligence.

Tracks product waste per session (actual vs expected usage),
generates eco scores, detects anomalies, and powers the Green Salon badge.
"""
from datetime import datetime, timezone, date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_db, generate_uuid
from utils.dependencies import get_current_user, require_role
from models.user import User, UserRole
from schemas.common import APIResponse

router = APIRouter(prefix="/eco", tags=["Eco Tracker"])


# ── Pydantic Schemas ──

class WasteLogEntry(BaseModel):
    session_id: str
    location_id: str
    stylist_id: str
    service_name: str
    product_name: str
    expected_quantity_ml: float
    actual_quantity_ml: float
    unit: str = "ml"
    eco_notes: Optional[str] = None


class EcoScoreUpdate(BaseModel):
    session_id: str
    customer_opt_in: bool = False  # customer chose to see their eco score


# ── Eco Score Calculator ──

def calculate_eco_score(expected: float, actual: float) -> dict:
    """Calculate eco score from product usage efficiency.

    Score 100 = zero waste (actual ≤ expected)
    Score 0   = extreme overuse (actual ≥ 3x expected)
    """
    if expected <= 0:
        return {"score": 50, "label": "Unknown", "waste_pct": 0, "is_anomaly": False}

    waste_pct = max(0, (actual - expected) / expected * 100)
    score = max(0, 100 - waste_pct)
    is_anomaly = actual >= expected * 2  # 2x overuse = anomaly alert

    if score >= 90:
        label = "Excellent"
    elif score >= 75:
        label = "Good"
    elif score >= 55:
        label = "Average"
    elif score >= 35:
        label = "Below Average"
    else:
        label = "Poor"

    return {
        "score": round(score, 1),
        "label": label,
        "waste_pct": round(waste_pct, 1),
        "is_anomaly": is_anomaly,
        "saved_ml": max(0, expected - actual),
        "wasted_ml": max(0, actual - expected),
    }


# ── Endpoints ──

@router.post("/log-waste", response_model=APIResponse)
async def log_product_waste(
    entry: WasteLogEntry,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Log actual vs expected product usage for a service session.
    Called by stylist at end of each service.
    Automatically triggers anomaly alert if usage ≥ 2x expected.
    """
    eco = calculate_eco_score(entry.expected_quantity_ml, entry.actual_quantity_ml)

    # Store in session JSON (uses existing sessions model products_used field)
    from models.session import ServiceSession
    session = await db.get(ServiceSession, entry.session_id)
    if not session:
        raise HTTPException(404, "Service session not found")

    products = session.products_used or []
    products.append({
        "product_name": entry.product_name,
        "service_name": entry.service_name,
        "expected_ml": entry.expected_quantity_ml,
        "actual_ml": entry.actual_quantity_ml,
        "unit": entry.unit,
        "eco_score": eco["score"],
        "eco_label": eco["label"],
        "waste_pct": eco["waste_pct"],
        "is_anomaly": eco["is_anomaly"],
        "logged_at": datetime.now(timezone.utc).isoformat(),
        "notes": entry.eco_notes,
    })
    session.products_used = products
    await db.commit()

    # Fire anomaly alert to manager if overuse detected
    if eco["is_anomaly"]:
        from tasks.eco_tasks import send_waste_anomaly_alert
        send_waste_anomaly_alert.delay(
            location_id=entry.location_id,
            session_id=entry.session_id,
            product_name=entry.product_name,
            expected=entry.expected_quantity_ml,
            actual=entry.actual_quantity_ml,
        )

    return APIResponse(
        success=True,
        message="Waste logged successfully",
        data={
            "eco_score": eco,
            "anomaly_alert_sent": eco["is_anomaly"],
        },
    )


@router.get("/session/{session_id}/eco-score", response_model=APIResponse)
async def get_session_eco_score(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the eco score summary for a completed session.
    Shown to customer at checkout if they opted in.
    """
    from models.session import ServiceSession
    session = await db.get(ServiceSession, session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    products = session.products_used or []
    if not products:
        return APIResponse(
            success=True,
            message="No product usage logged for this session",
            data={"eco_score": None, "products": []},
        )

    eco_entries = [p for p in products if "eco_score" in p]
    if not eco_entries:
        return APIResponse(
            success=True,
            message="No eco data available",
            data={"eco_score": None},
        )

    avg_score = sum(p["eco_score"] for p in eco_entries) / len(eco_entries)
    total_wasted = sum(p.get("wasted_ml", 0) for p in eco_entries)

    return APIResponse(
        success=True,
        message="Session eco score",
        data={
            "session_id": session_id,
            "overall_eco_score": round(avg_score, 1),
            "total_products_tracked": len(eco_entries),
            "total_wasted_ml": round(total_wasted, 1),
            "products": eco_entries,
            "carbon_saved_estimate_g": round(total_wasted * 0.003, 2),
        },
    )


@router.get("/location/{location_id}/dashboard", response_model=APIResponse)
async def location_eco_dashboard(
    location_id: str,
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None),
    current_user: User = Depends(require_role([UserRole.SALON_MANAGER, UserRole.FRANCHISE_OWNER,
                                               UserRole.REGIONAL_MANAGER, UserRole.SUPER_ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """Location-level eco dashboard: monthly waste trends, stylist breakdown, anomaly count."""
    from models.session import ServiceSession
    from models.booking import Booking

    target_month = month or datetime.now().month
    target_year = year or datetime.now().year

    # Pull all sessions for this location in the target month
    month_start = datetime(target_year, target_month, 1, tzinfo=timezone.utc)
    if target_month == 12:
        month_end = datetime(target_year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        month_end = datetime(target_year, target_month + 1, 1, tzinfo=timezone.utc)

    sessions_result = await db.execute(
        select(ServiceSession)
        .join(Booking, ServiceSession.booking_id == Booking.id)
        .where(
            Booking.location_id == location_id,
            ServiceSession.started_at >= month_start,
            ServiceSession.started_at < month_end,
        )
    )
    sessions = sessions_result.scalars().all()

    all_products = []
    anomaly_count = 0
    for s in sessions:
        for p in (s.products_used or []):
            if "eco_score" in p:
                all_products.append(p)
                if p.get("is_anomaly"):
                    anomaly_count += 1

    avg_score = (
        sum(p["eco_score"] for p in all_products) / len(all_products)
        if all_products else 0
    )

    return APIResponse(
        success=True,
        message="Location eco dashboard",
        data={
            "location_id": location_id,
            "month": target_month,
            "year": target_year,
            "avg_eco_score": round(avg_score, 1),
            "total_sessions_tracked": len(sessions),
            "products_logged": len(all_products),
            "anomalies_detected": anomaly_count,
            "total_waste_ml": round(sum(p.get("wasted_ml", 0) for p in all_products), 1),
        },
    )


@router.get("/green-salon-leaderboard", response_model=APIResponse)
async def green_salon_leaderboard(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Network-wide Green Salon of the Month leaderboard.
    Ranked by average eco score across all sessions in the month.
    """
    from models.location import Location
    from models.session import ServiceSession
    from models.booking import Booking

    target_month = month or datetime.now().month
    target_year = year or datetime.now().year

    month_start = datetime(target_year, target_month, 1, tzinfo=timezone.utc)
    if target_month == 12:
        month_end = datetime(target_year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        month_end = datetime(target_year, target_month + 1, 1, tzinfo=timezone.utc)

    locations_result = await db.execute(select(Location).where(Location.is_active == True))
    locations = locations_result.scalars().all()

    leaderboard = []
    for loc in locations:
        sessions_result = await db.execute(
            select(ServiceSession)
            .join(Booking, ServiceSession.booking_id == Booking.id)
            .where(
                Booking.location_id == loc.id,
                ServiceSession.started_at >= month_start,
                ServiceSession.started_at < month_end,
            )
        )
        sessions = sessions_result.scalars().all()

        all_products = []
        for s in sessions:
            for p in (s.products_used or []):
                if "eco_score" in p:
                    all_products.append(p)

        if all_products:
            avg = sum(p["eco_score"] for p in all_products) / len(all_products)
            leaderboard.append({
                "location_id": loc.id,
                "location_name": loc.name,
                "city": getattr(loc, "city", ""),
                "avg_eco_score": round(avg, 1),
                "sessions_tracked": len(sessions),
                "products_logged": len(all_products),
            })

    leaderboard.sort(key=lambda x: x["avg_eco_score"], reverse=True)
    ranked = [{"rank": i + 1, **entry} for i, entry in enumerate(leaderboard[:limit])]

    winner = ranked[0] if ranked else None
    return APIResponse(
        success=True,
        message=f"Green Salon leaderboard for {target_month}/{target_year}",
        data={
            "month": target_month,
            "year": target_year,
            "green_salon_of_the_month": winner,
            "leaderboard": ranked,
        },
    )
