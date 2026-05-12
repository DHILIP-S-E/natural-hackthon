"""AI Franchise Performance Dashboard — Idea 18: 750-Branch Visibility.

Domain logic:
  HQ-level multi-branch analytics with:
  - Revenue trend per branch (this week vs last week, WoW %)
  - AuraScore aggregate per branch (quality heatmap)
  - Staff attrition risk flag count per branch
  - Inventory alert count per branch
  - Customer retention rate per branch
  - Automatic anomaly detection: branch revenue drop > 20% WoW → alert
  - Clustering: group underperformers by root cause
    (staff_risk / inventory / low_demand / quality)
  - Top 10 / Bottom 10 salon rankings by retention rate
  - Weekly digest generation for regional managers
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_role
from app.models.user import User, UserRole
from app.schemas.common import APIResponse

router = APIRouter(prefix="/franchise-dashboard", tags=["AI Franchise Performance Dashboard"])

REVENUE_DROP_THRESHOLD = 0.20  # 20% WoW drop triggers alert


def _classify_underperformer(
    revenue_drop_pct: float,
    attrition_risk_count: int,
    inventory_alert_count: int,
    aurascore_avg: float,
) -> str:
    """Simple rule-based root cause clustering."""
    if attrition_risk_count >= 2:
        return "staff_risk"
    if inventory_alert_count >= 3:
        return "inventory"
    if aurascore_avg < 60:
        return "quality"
    if revenue_drop_pct > 0.30:
        return "low_demand"
    return "multiple_factors"


async def _get_branch_revenue(location_id: str, start: datetime, end: datetime, db: AsyncSession) -> float:
    from app.models.booking import Booking
    from sqlalchemy import and_
    result = await db.execute(
        select(func.coalesce(func.sum(Booking.total_amount), 0))
        .where(
            Booking.location_id == location_id,
            Booking.scheduled_at >= start,
            Booking.scheduled_at < end,
            Booking.status.in_(["completed", "COMPLETED"]),
        )
    )
    return float(result.scalar() or 0)


async def _get_branch_aurascore(location_id: str, db: AsyncSession) -> float:
    from app.models.quality import QualityAssessment
    from app.models.booking import Booking
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(func.avg(QualityAssessment.overall_score))
        .join(Booking, QualityAssessment.booking_id == Booking.id)
        .where(
            Booking.location_id == location_id,
            QualityAssessment.created_at >= now - timedelta(days=30),
            QualityAssessment.overall_score.isnot(None),
        )
    )
    return float(result.scalar() or 75.0)


async def _get_attrition_risk_count(location_id: str, db: AsyncSession) -> int:
    from app.models.staff import StaffProfile
    result = await db.execute(
        select(func.count(StaffProfile.id)).where(
            StaffProfile.location_id == location_id,
            StaffProfile.attrition_risk_score >= 0.6,
        )
    )
    return int(result.scalar() or 0)


async def _get_inventory_alert_count(location_id: str, db: AsyncSession) -> int:
    from app.models.inventory import InventoryItem
    try:
        result = await db.execute(
            select(func.count(InventoryItem.id)).where(
                InventoryItem.location_id == location_id,
                InventoryItem.current_stock <= InventoryItem.reorder_level,
            )
        )
        return int(result.scalar() or 0)
    except Exception:
        return 0


async def _get_retention_rate(location_id: str, db: AsyncSession) -> float:
    from app.models.booking import Booking
    from app.models.customer import CustomerProfile
    now = datetime.now(timezone.utc)
    ninety_days_ago = now - timedelta(days=90)
    thirty_days_ago = now - timedelta(days=30)

    # Customers who visited in 60-90 day window
    cohort_result = await db.execute(
        select(func.count(func.distinct(Booking.customer_id))).where(
            Booking.location_id == location_id,
            Booking.scheduled_at >= ninety_days_ago,
            Booking.scheduled_at < now - timedelta(days=60),
            Booking.status.in_(["completed", "COMPLETED"]),
        )
    )
    cohort = int(cohort_result.scalar() or 0)
    if cohort == 0:
        return 0.0

    # Of those, how many returned in last 30 days
    returned_result = await db.execute(
        select(func.count(func.distinct(Booking.customer_id))).where(
            Booking.location_id == location_id,
            Booking.scheduled_at >= thirty_days_ago,
            Booking.status.in_(["completed", "COMPLETED"]),
        )
    )
    returned = int(returned_result.scalar() or 0)
    return round(min(100, (returned / cohort) * 100), 1)


@router.get("/overview", response_model=APIResponse)
async def get_network_overview(
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.REGIONAL_MANAGER])),
    db: AsyncSession = Depends(get_db),
):
    """HQ-level: all branches at a glance — revenue, quality, staff risk, inventory.
    Powers the corporate performance map and top/bottom 10 leaderboard.
    """
    from app.models.location import Location

    now = datetime.now(timezone.utc)
    this_week_start = now - timedelta(days=7)
    last_week_start = now - timedelta(days=14)
    last_week_end = this_week_start

    locations_result = await db.execute(
        select(Location).where(Location.is_active == True)
    )
    locations = locations_result.scalars().all()

    branches = []
    anomalies = []
    total_revenue_this_week = 0.0
    total_revenue_last_week = 0.0

    for loc in locations:
        lid = str(loc.id)

        rev_this = await _get_branch_revenue(lid, this_week_start, now, db)
        rev_last = await _get_branch_revenue(lid, last_week_start, last_week_end, db)
        wow_pct = ((rev_this - rev_last) / max(1, rev_last)) * 100 if rev_last else 0

        aurascore = await _get_branch_aurascore(lid, db)
        attrition_count = await _get_attrition_risk_count(lid, db)
        inv_alerts = await _get_inventory_alert_count(lid, db)
        retention = await _get_retention_rate(lid, db)

        entry = {
            "location_id": lid,
            "name": loc.name,
            "city": loc.city,
            "state": getattr(loc, "state", ""),
            "revenue_this_week": rev_this,
            "revenue_last_week": rev_last,
            "revenue_wow_pct": round(wow_pct, 1),
            "aurascore_avg": round(aurascore, 1),
            "attrition_risk_staff": attrition_count,
            "inventory_alerts": inv_alerts,
            "retention_rate_pct": retention,
            "status": (
                "critical" if wow_pct < -REVENUE_DROP_THRESHOLD * 100
                else "at_risk" if (attrition_count >= 2 or inv_alerts >= 3)
                else "healthy"
            ),
        }
        branches.append(entry)
        total_revenue_this_week += rev_this
        total_revenue_last_week += rev_last

        # Anomaly: revenue drop > 20%
        if rev_last > 0 and wow_pct < -(REVENUE_DROP_THRESHOLD * 100):
            root_cause = _classify_underperformer(
                revenue_drop_pct=abs(wow_pct) / 100,
                attrition_risk_count=attrition_count,
                inventory_alert_count=inv_alerts,
                aurascore_avg=aurascore,
            )
            anomalies.append({
                "location_id": lid,
                "name": loc.name,
                "city": loc.city,
                "revenue_drop_pct": round(abs(wow_pct), 1),
                "root_cause": root_cause,
                "recommended_action": _get_action(root_cause),
            })

    # Sort by retention for leaderboard
    by_retention = sorted(branches, key=lambda b: b["retention_rate_pct"], reverse=True)
    by_revenue = sorted(branches, key=lambda b: b["revenue_this_week"], reverse=True)
    by_quality = sorted(branches, key=lambda b: b["aurascore_avg"], reverse=True)

    network_wow = ((total_revenue_this_week - total_revenue_last_week) / max(1, total_revenue_last_week)) * 100

    return APIResponse(
        success=True,
        message="Network performance overview",
        data={
            "total_branches": len(branches),
            "network_revenue_this_week": total_revenue_this_week,
            "network_revenue_wow_pct": round(network_wow, 1),
            "critical_branches": sum(1 for b in branches if b["status"] == "critical"),
            "at_risk_branches": sum(1 for b in branches if b["status"] == "at_risk"),
            "anomalies": anomalies,
            "top_10_by_retention": by_retention[:10],
            "bottom_10_by_retention": by_retention[-10:][::-1],
            "top_10_by_revenue": by_revenue[:10],
            "top_10_by_quality": by_quality[:10],
            "branches": branches,
        },
    )


def _get_action(root_cause: str) -> str:
    actions = {
        "staff_risk": "Schedule retention meeting. Check if any senior stylists are due for a review.",
        "inventory": "Trigger emergency stock reorder. Contact supplier for expedited delivery.",
        "quality": "Deploy QA team for on-site AuraScore coaching visit this week.",
        "low_demand": "Run a hyperlocal WhatsApp campaign with walk-in friendly pricing.",
        "multiple_factors": "Regional manager to conduct full branch audit within 48 hours.",
    }
    return actions.get(root_cause, "Review branch with regional manager.")


@router.get("/branch/{location_id}", response_model=APIResponse)
async def get_branch_detail(
    location_id: str,
    current_user: User = Depends(require_role([
        UserRole.SUPER_ADMIN, UserRole.REGIONAL_MANAGER, UserRole.FRANCHISE_OWNER, UserRole.SALON_MANAGER
    ])),
    db: AsyncSession = Depends(get_db),
):
    """Drill-down: full branch analytics for a single location."""
    from app.models.location import Location
    from app.models.booking import Booking
    from sqlalchemy import extract

    now = datetime.now(timezone.utc)
    loc = await db.get(Location, location_id)
    if not loc:
        from fastapi import HTTPException
        raise HTTPException(404, "Location not found")

    # 8-week revenue trend
    weekly_revenue = []
    for weeks_ago in range(7, -1, -1):
        start = now - timedelta(days=(weeks_ago + 1) * 7)
        end = now - timedelta(days=weeks_ago * 7)
        rev = await _get_branch_revenue(location_id, start, end, db)
        week_label = start.strftime("%b %d")
        weekly_revenue.append({"week": week_label, "revenue": rev})

    # This week metrics
    rev_this = await _get_branch_revenue(location_id, now - timedelta(days=7), now, db)
    rev_last = await _get_branch_revenue(location_id, now - timedelta(days=14), now - timedelta(days=7), db)
    wow_pct = ((rev_this - rev_last) / max(1, rev_last)) * 100 if rev_last else 0
    aurascore = await _get_branch_aurascore(location_id, db)
    attrition = await _get_attrition_risk_count(location_id, db)
    inv_alerts = await _get_inventory_alert_count(location_id, db)
    retention = await _get_retention_rate(location_id, db)

    # Service mix this month
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    svc_result = await db.execute(
        select(Booking.service_id, func.count(Booking.id).label("cnt"))
        .where(
            Booking.location_id == location_id,
            Booking.scheduled_at >= month_start,
            Booking.status.in_(["completed", "COMPLETED"]),
        )
        .group_by(Booking.service_id)
        .order_by(func.count(Booking.id).desc())
        .limit(5)
    )
    service_mix = [{"service_id": str(r.service_id), "count": r.cnt} for r in svc_result.all()]

    return APIResponse(
        success=True,
        message="Branch detail analytics",
        data={
            "location_id": location_id,
            "name": loc.name,
            "city": loc.city,
            "revenue_this_week": rev_this,
            "revenue_wow_pct": round(wow_pct, 1),
            "aurascore_avg": round(aurascore, 1),
            "attrition_risk_staff": attrition,
            "inventory_alerts": inv_alerts,
            "retention_rate_pct": retention,
            "weekly_revenue_trend": weekly_revenue,
            "top_services_this_month": service_mix,
            "status": (
                "critical" if wow_pct < -20
                else "at_risk" if (attrition >= 2 or inv_alerts >= 3)
                else "healthy"
            ),
        },
    )


@router.get("/weekly-digest", response_model=APIResponse)
async def get_weekly_digest(
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.REGIONAL_MANAGER])),
    db: AsyncSession = Depends(get_db),
):
    """Auto-generate weekly digest for regional manager.
    Summarises network health, top performers, anomalies.
    """
    from app.config import settings
    from app.services.ai_service import _call_gemini, _call_openai
    from app.models.location import Location

    now = datetime.now(timezone.utc)
    locations_result = await db.execute(select(Location).where(Location.is_active == True))
    locations = locations_result.scalars().all()

    top_branches = []
    problem_branches = []

    for loc in locations[:20]:  # sample for digest
        lid = str(loc.id)
        rev = await _get_branch_revenue(lid, now - timedelta(days=7), now, db)
        rev_last = await _get_branch_revenue(lid, now - timedelta(days=14), now - timedelta(days=7), db)
        wow = ((rev - rev_last) / max(1, rev_last)) * 100 if rev_last else 0
        if wow >= 10:
            top_branches.append(f"{loc.name} ({loc.city}): +{wow:.0f}% WoW")
        elif wow < -20:
            problem_branches.append(f"{loc.name} ({loc.city}): {wow:.0f}% WoW")

    prompt = (
        f"You are AURA's regional intelligence system. Write a concise weekly digest (max 150 words) "
        f"for regional managers of Naturals salon network.\n"
        f"Date: {now.strftime('%d %B %Y')}\n"
        f"Top performing branches: {', '.join(top_branches[:3]) or 'None highlighted this week'}\n"
        f"Branches needing attention: {', '.join(problem_branches[:3]) or 'No critical issues'}\n"
        f"Format: 3 bullets: Network Pulse, Top Performers, Attention Required. Professional, data-driven tone."
    )

    try:
        if settings.AI_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
            digest = await _call_gemini(prompt)
        elif settings.OPENAI_API_KEY:
            digest = await _call_openai(prompt)
        else:
            digest = (
                f"• Network Pulse: {len(locations)} branches active. "
                f"{len(problem_branches)} require immediate attention.\n"
                f"• Top Performers: {', '.join(top_branches[:2]) or 'Stable across network'}.\n"
                f"• Attention Required: {', '.join(problem_branches[:2]) or 'No critical revenue drops.'}"
            )
    except Exception:
        digest = "Weekly digest generation pending. Review branch overview for details."

    return APIResponse(
        success=True,
        message="Weekly digest ready",
        data={
            "generated_at": now.isoformat(),
            "digest": digest,
            "top_performers": top_branches[:5],
            "problem_branches": problem_branches[:5],
        },
    )
