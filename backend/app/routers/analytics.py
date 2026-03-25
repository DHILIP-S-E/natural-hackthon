"""Analytics & BI router — complete analytics endpoints per aura.md spec."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, case, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timezone, timedelta

from app.database import get_db
from app.models.user import User, UserRole
from app.models.booking import Booking, BookingStatus
from app.models.quality import QualityAssessment
from app.models.soulskin import SoulskinSession
from app.models.feedback import CustomerFeedback
from app.models.customer import CustomerProfile
from app.models.staff import StaffProfile
from app.models.training import TrainingRecord
from app.models.service import Service
from app.models.location import Location
from app.dependencies import get_current_user, require_any_staff, require_roles
from app.schemas.common import APIResponse

# Track 6 AI Agent Handlers
from app.agents.track6_intelligence import (
    franchise_bi_dashboard_handler,
    training_roi_handler as ai_training_roi_handler,
    franchise_live_compare_handler,
    customer_ltv_model_handler,
    skill_gap_forecast_handler as ai_skill_gap_forecast_handler,
)


router = APIRouter(prefix="/analytics", tags=["Analytics & BI"])


def _location_filter(query, model, location_id: Optional[str]):
    """Helper to add location_id filter if provided."""
    if location_id and hasattr(model, 'location_id'):
        return query.where(model.location_id == location_id)
    return query


@router.get("/overview", response_model=APIResponse)
async def analytics_overview(
    location_id: Optional[str] = None,
    current_user: User = Depends(require_any_staff()),
    db: AsyncSession = Depends(get_db),
):
    """Get overview analytics for dashboard."""
    # Combined booking stats in a single query using CASE expressions
    booking_agg = select(
        func.count().label("total"),
        func.sum(case((Booking.status == BookingStatus.COMPLETED, 1), else_=0)).label("completed"),
        func.sum(case((Booking.status == BookingStatus.NO_SHOW, 1), else_=0)).label("no_shows"),
        func.sum(case((Booking.status == BookingStatus.COMPLETED, Booking.final_price), else_=0)).label("revenue"),
    )
    if location_id:
        booking_agg = booking_agg.where(Booking.location_id == location_id)
    brow = (await db.execute(booking_agg)).one()
    total_bookings = brow.total or 0
    completed = int(brow.completed or 0)
    no_shows = int(brow.no_shows or 0)
    total_revenue = float(brow.revenue or 0)

    # Quality + feedback + soulskin + customers in parallel-ish (3 remaining queries)
    quality_q = select(func.avg(QualityAssessment.overall_score))
    feedback_q = select(func.avg(CustomerFeedback.overall_rating))
    soulskin_q = select(func.count()).select_from(SoulskinSession).where(SoulskinSession.session_completed == True)
    if location_id:
        quality_q = quality_q.where(QualityAssessment.location_id == location_id)
        feedback_q = feedback_q.where(CustomerFeedback.location_id == location_id)
        soulskin_q = soulskin_q.where(SoulskinSession.location_id == location_id)

    avg_quality = (await db.execute(quality_q)).scalar() or 0
    avg_rating = (await db.execute(feedback_q)).scalar() or 0
    soulskin_count = (await db.execute(soulskin_q)).scalar() or 0
    total_customers = (await db.execute(select(func.count()).select_from(CustomerProfile))).scalar() or 0

    return APIResponse(success=True, data={
        "total_bookings": total_bookings,
        "completed_bookings": completed,
        "total_revenue": total_revenue,
        "avg_quality_score": round(float(avg_quality), 2) if avg_quality else 0,
        "soulskin_sessions": soulskin_count,
        "total_customers": total_customers,
        "avg_customer_rating": round(float(avg_rating), 1) if avg_rating else 0,
        "no_shows": no_shows,
        "completion_rate": round(completed / total_bookings * 100, 1) if total_bookings > 0 else 0,
    })


@router.get("/revenue", response_model=APIResponse)
async def revenue_analytics(
    location_id: Optional[str] = None,
    days: int = 30,
    current_user: User = Depends(require_any_staff()),
    db: AsyncSession = Depends(get_db),
):
    """Revenue breakdown by day, service category, and location."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    # Total revenue in period
    rev_q = select(func.sum(Booking.final_price)).where(
        Booking.status == BookingStatus.COMPLETED,
        Booking.created_at >= cutoff,
    )
    if location_id:
        rev_q = rev_q.where(Booking.location_id == location_id)
    total = (await db.execute(rev_q)).scalar() or 0

    # Revenue by service category
    cat_q = (
        select(Service.category, func.sum(Booking.final_price), func.count())
        .join(Service, Booking.service_id == Service.id)
        .where(Booking.status == BookingStatus.COMPLETED, Booking.created_at >= cutoff)
        .group_by(Service.category)
    )
    if location_id:
        cat_q = cat_q.where(Booking.location_id == location_id)
    cat_result = await db.execute(cat_q)
    by_category = [{"category": r[0], "revenue": float(r[1] or 0), "count": r[2]} for r in cat_result.all()]

    # Revenue by location
    loc_q = (
        select(Location.name, func.sum(Booking.final_price), func.count())
        .join(Location, Booking.location_id == Location.id)
        .where(Booking.status == BookingStatus.COMPLETED, Booking.created_at >= cutoff)
        .group_by(Location.name)
    )
    loc_result = await db.execute(loc_q)
    by_location = [{"location": r[0], "revenue": float(r[1] or 0), "bookings": r[2]} for r in loc_result.all()]

    return APIResponse(success=True, data={
        "period_days": days,
        "total_revenue": float(total),
        "by_category": by_category,
        "by_location": by_location,
    })


@router.get("/quality", response_model=APIResponse)
async def quality_analytics(
    location_id: Optional[str] = None,
    days: int = 30,
    current_user: User = Depends(require_any_staff()),
    db: AsyncSession = Depends(get_db),
):
    """Quality metrics — average scores, flagged sessions, compliance trends."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    base = select(QualityAssessment).where(QualityAssessment.created_at >= cutoff)
    if location_id:
        base = base.where(QualityAssessment.location_id == location_id)

    # Aggregate scores
    agg_q = select(
        func.avg(QualityAssessment.overall_score),
        func.avg(QualityAssessment.sop_compliance_score),
        func.avg(QualityAssessment.timing_score),
        func.avg(QualityAssessment.customer_rating),
        func.count(),
        func.sum(case((QualityAssessment.is_flagged == True, 1), else_=0)),
    ).where(QualityAssessment.created_at >= cutoff)
    if location_id:
        agg_q = agg_q.where(QualityAssessment.location_id == location_id)
    row = (await db.execute(agg_q)).one()

    return APIResponse(success=True, data={
        "avg_overall_score": round(float(row[0] or 0), 2),
        "avg_sop_compliance": round(float(row[1] or 0), 2),
        "avg_timing_score": round(float(row[2] or 0), 2),
        "avg_customer_rating": round(float(row[3] or 0), 1),
        "total_assessments": row[4],
        "flagged_count": int(row[5] or 0),
        "flagged_pct": round(int(row[5] or 0) / row[4] * 100, 1) if row[4] > 0 else 0,
    })


@router.get("/staff", response_model=APIResponse)
async def staff_analytics(
    location_id: Optional[str] = None,
    current_user: User = Depends(require_any_staff()),
    db: AsyncSession = Depends(get_db),
):
    """Staff performance leaderboard — services, revenue, quality per stylist."""
    # Join StaffProfile with User to avoid N+1
    q = (
        select(StaffProfile, User.first_name, User.last_name)
        .join(User, StaffProfile.user_id == User.id)
        .where(StaffProfile.is_available == True)
    )
    if location_id:
        q = q.where(StaffProfile.location_id == location_id)
    result = await db.execute(q)
    rows = result.all()

    staff_data = []
    for s, first_name, last_name in rows:
        name = f"{first_name} {last_name}" if first_name else "Unknown"
        staff_data.append({
            "id": s.id, "name": name,
            "skill_level": s.skill_level,
            "total_services": s.total_services_done,
            "total_revenue": float(s.total_revenue_generated or 0),
            "current_rating": float(s.current_rating or 0),
            "soulskin_certified": s.soulskin_certified,
            "attrition_risk": s.attrition_risk_label,
            "specializations": s.specializations or [],
        })

    staff_data.sort(key=lambda x: x["total_revenue"], reverse=True)

    return APIResponse(success=True, data={"staff": staff_data, "total_staff": len(staff_data)})


@router.get("/customers", response_model=APIResponse)
async def customer_analytics(
    location_id: Optional[str] = None,
    current_user: User = Depends(require_any_staff()),
    db: AsyncSession = Depends(get_db),
):
    """Customer analytics — segments, LTV distribution, archetype breakdown."""
    total = (await db.execute(select(func.count()).select_from(CustomerProfile))).scalar() or 0

    # LTV tiers
    ltv_q = select(
        func.sum(case((CustomerProfile.lifetime_value >= 50000, 1), else_=0)),
        func.sum(case((CustomerProfile.lifetime_value.between(20000, 49999), 1), else_=0)),
        func.sum(case((CustomerProfile.lifetime_value.between(5000, 19999), 1), else_=0)),
        func.sum(case((CustomerProfile.lifetime_value < 5000, 1), else_=0)),
    )
    ltv = (await db.execute(ltv_q)).one()

    # Archetype distribution
    arch_q = select(CustomerProfile.dominant_archetype, func.count()).where(
        CustomerProfile.dominant_archetype.isnot(None)
    ).group_by(CustomerProfile.dominant_archetype)
    arch_result = await db.execute(arch_q)
    archetypes = {r[0]: r[1] for r in arch_result.all()}

    # Avg beauty score
    avg_score = (await db.execute(select(func.avg(CustomerProfile.beauty_score)))).scalar() or 0

    return APIResponse(success=True, data={
        "total_customers": total,
        "ltv_tiers": {
            "gold": int(ltv[0] or 0), "silver": int(ltv[1] or 0),
            "bronze": int(ltv[2] or 0), "new": int(ltv[3] or 0),
        },
        "archetype_distribution": archetypes,
        "avg_beauty_score": round(float(avg_score), 1),
    })


@router.get("/training-roi", response_model=APIResponse)
async def training_roi(
    current_user: User = Depends(require_any_staff()),
    db: AsyncSession = Depends(get_db),
):
    """Training investment ROI — cost vs revenue/quality impact."""
    result = await db.execute(select(TrainingRecord).order_by(TrainingRecord.created_at.desc()).limit(50))
    records = result.scalars().all()

    total_cost = sum(float(r.cost_to_company or 0) for r in records)
    total_hours = sum(float(r.hours_completed or 0) for r in records)
    pass_rate = sum(1 for r in records if r.passed) / len(records) * 100 if records else 0

    # ROI: compare revenue before/after training
    roi_records = [r for r in records if r.revenue_before and r.revenue_after]
    avg_revenue_lift = 0
    if roi_records:
        lifts = [float(r.revenue_after - r.revenue_before) for r in roi_records]
        avg_revenue_lift = sum(lifts) / len(lifts)

    return APIResponse(success=True, data={
        "total_training_records": len(records),
        "total_investment": total_cost,
        "total_hours": total_hours,
        "pass_rate": round(pass_rate, 1),
        "avg_revenue_lift_per_stylist": round(avg_revenue_lift, 2),
        "soulskin_trained": sum(1 for r in records if r.includes_soulskin),
    })


@router.get("/attrition", response_model=APIResponse)
async def attrition_analytics(
    location_id: Optional[str] = None,
    current_user: User = Depends(require_any_staff()),
    db: AsyncSession = Depends(get_db),
):
    """Staff attrition risk overview."""
    # Join with User to avoid N+1 for high-risk staff names
    q = (
        select(StaffProfile, User.first_name, User.last_name)
        .join(User, StaffProfile.user_id == User.id)
    )
    if location_id:
        q = q.where(StaffProfile.location_id == location_id)
    result = await db.execute(q)
    rows = result.all()

    risk_counts = {"low": 0, "medium": 0, "high": 0}
    high_risk_staff = []
    for s, first_name, last_name in rows:
        risk = s.attrition_risk_label or "low"
        risk_counts[risk] = risk_counts.get(risk, 0) + 1
        if risk == "high":
            high_risk_staff.append({
                "id": s.id,
                "name": f"{first_name} {last_name}" if first_name else "Unknown",
                "risk_score": float(s.attrition_risk_score or 0),
                "skill_level": s.skill_level,
            })

    return APIResponse(success=True, data={
        "total_staff": len(rows),
        "risk_distribution": risk_counts,
        "high_risk_staff": high_risk_staff,
    })


@router.get("/compare", response_model=APIResponse)
async def compare_locations(
    current_user: User = Depends(require_any_staff()),
    db: AsyncSession = Depends(get_db),
):
    """Side-by-side location comparison."""
    loc_result = await db.execute(select(Location).where(Location.is_active == True))
    locations = loc_result.scalars().all()

    # Batch-fetch all metrics per location in 3 queries instead of 4*N
    loc_ids = [loc.id for loc in locations]

    # Revenue + booking count per location
    rev_q = (
        select(
            Booking.location_id,
            func.sum(Booking.final_price),
            func.count(),
        )
        .where(Booking.location_id.in_(loc_ids))
        .group_by(Booking.location_id)
    )
    rev_result = await db.execute(rev_q)
    rev_map: dict = {}
    bookings_map: dict = {}
    for loc_id, rev, cnt in rev_result.all():
        rev_map[loc_id] = float(rev or 0)
        bookings_map[loc_id] = cnt

    # Completed-only revenue
    rev_completed_q = (
        select(Booking.location_id, func.sum(Booking.final_price))
        .where(Booking.location_id.in_(loc_ids), Booking.status == BookingStatus.COMPLETED)
        .group_by(Booking.location_id)
    )
    rev_completed = {row[0]: float(row[1] or 0) for row in (await db.execute(rev_completed_q)).all()}

    # Quality per location
    qual_q = (
        select(QualityAssessment.location_id, func.avg(QualityAssessment.overall_score))
        .where(QualityAssessment.location_id.in_(loc_ids))
        .group_by(QualityAssessment.location_id)
    )
    qual_map = {row[0]: float(row[1] or 0) for row in (await db.execute(qual_q)).all()}

    # SOULSKIN per location
    ss_q = (
        select(SoulskinSession.location_id, func.count())
        .where(SoulskinSession.location_id.in_(loc_ids), SoulskinSession.session_completed == True)
        .group_by(SoulskinSession.location_id)
    )
    ss_map = {row[0]: row[1] for row in (await db.execute(ss_q)).all()}

    comparisons = []
    for loc in locations:
        comparisons.append({
            "id": loc.id, "name": loc.name, "code": loc.code, "city": loc.city,
            "revenue": rev_completed.get(loc.id, 0),
            "avg_quality": round(qual_map.get(loc.id, 0), 2),
            "total_bookings": bookings_map.get(loc.id, 0),
            "soulskin_sessions": ss_map.get(loc.id, 0),
            "target": float(loc.monthly_revenue_target or 0),
        })

    comparisons.sort(key=lambda x: x["revenue"], reverse=True)
    return APIResponse(success=True, data={"locations": comparisons})


@router.get("/soulskin", response_model=APIResponse)
async def soulskin_analytics(
    location_id: Optional[str] = None,
    current_user: User = Depends(require_any_staff()),
    db: AsyncSession = Depends(get_db),
):
    """SOULSKIN analytics — archetype distribution, impact on ratings."""
    arch_q = (
        select(SoulskinSession.archetype, func.count())
        .where(SoulskinSession.session_completed == True, SoulskinSession.archetype.isnot(None))
        .group_by(SoulskinSession.archetype)
    )
    if location_id:
        arch_q = arch_q.where(SoulskinSession.location_id == location_id)
    result = await db.execute(arch_q)
    distribution = {row[0]: row[1] for row in result.all()}

    # SOULSKIN impact: avg rating WITH vs WITHOUT
    with_q = select(func.avg(CustomerFeedback.overall_rating)).where(
        CustomerFeedback.soulskin_session_id.isnot(None)
    )
    without_q = select(func.avg(CustomerFeedback.overall_rating)).where(
        CustomerFeedback.soulskin_session_id.is_(None)
    )
    if location_id:
        with_q = with_q.where(CustomerFeedback.location_id == location_id)
        without_q = without_q.where(CustomerFeedback.location_id == location_id)

    avg_with = (await db.execute(with_q)).scalar() or 0
    avg_without = (await db.execute(without_q)).scalar() or 0

    return APIResponse(success=True, data={
        "archetype_distribution": distribution,
        "total_sessions": sum(distribution.values()),
        "avg_rating_with_soulskin": round(float(avg_with), 2) if avg_with else 0,
        "avg_rating_without_soulskin": round(float(avg_without), 2) if avg_without else 0,
        "rating_lift": round(float(avg_with) - float(avg_without), 2) if avg_with and avg_without else 0,
    })


@router.get("/skill-gap", response_model=APIResponse)
async def skill_gap_analysis(
    current_user: User = Depends(require_any_staff()),
    db: AsyncSession = Depends(get_db),
):
    """Skill gap forecasting — current skill levels vs service demand."""
    # Staff skill distribution
    skill_q = select(StaffProfile.skill_level, func.count()).group_by(StaffProfile.skill_level)
    skill_result = await db.execute(skill_q)
    skills = {r[0]: r[1] for r in skill_result.all()}

    # Service demand by skill requirement
    svc_q = select(Service.skill_required, func.count()).group_by(Service.skill_required)
    svc_result = await db.execute(svc_q)
    demand = {r[0]: r[1] for r in svc_result.all()}

    # SOULSKIN certification
    certified = (await db.execute(
        select(func.count()).select_from(StaffProfile).where(StaffProfile.soulskin_certified == True)
    )).scalar() or 0
    total_staff = sum(skills.values())

    return APIResponse(success=True, data={
        "skill_distribution": skills,
        "service_demand_by_skill": demand,
        "soulskin_certified": certified,
        "soulskin_certification_rate": round(certified / total_staff * 100, 1) if total_staff > 0 else 0,
        "total_staff": total_staff,
    })


@router.get("/forecast", response_model=APIResponse)
async def revenue_forecast(
    location_id: Optional[str] = None,
    current_user: User = Depends(require_any_staff()),
    db: AsyncSession = Depends(get_db),
):
    """Simple revenue forecast based on recent trends."""
    # Last 30 days revenue
    cutoff_30 = datetime.now(timezone.utc) - timedelta(days=30)
    cutoff_60 = datetime.now(timezone.utc) - timedelta(days=60)

    rev_30_q = select(func.sum(Booking.final_price)).where(
        Booking.status == BookingStatus.COMPLETED, Booking.created_at >= cutoff_30
    )
    rev_60_q = select(func.sum(Booking.final_price)).where(
        Booking.status == BookingStatus.COMPLETED,
        Booking.created_at >= cutoff_60, Booking.created_at < cutoff_30
    )
    if location_id:
        rev_30_q = rev_30_q.where(Booking.location_id == location_id)
        rev_60_q = rev_60_q.where(Booking.location_id == location_id)

    rev_30 = float((await db.execute(rev_30_q)).scalar() or 0)
    rev_60 = float((await db.execute(rev_60_q)).scalar() or 0)

    growth_rate = (rev_30 - rev_60) / rev_60 if rev_60 > 0 else 0
    forecast_30 = rev_30 * (1 + growth_rate)

    return APIResponse(success=True, data={
        "last_30_days": rev_30,
        "previous_30_days": rev_60,
        "growth_rate": round(growth_rate * 100, 1),
        "forecast_next_30_days": round(forecast_30, 2),
        "trend": "growing" if growth_rate > 0.05 else "declining" if growth_rate < -0.05 else "stable",
    })


@router.post("/export", response_model=APIResponse)
async def export_report(
    report_type: str = "overview",
    location_id: Optional[str] = None,
    current_user: User = Depends(require_any_staff()),
    db: AsyncSession = Depends(get_db),
):
    """Export analytics report (returns data for client-side PDF/CSV generation)."""
    # Reuse existing analytics endpoints
    if report_type == "revenue":
        return await revenue_analytics(location_id=location_id, current_user=current_user, db=db)
    elif report_type == "quality":
        return await quality_analytics(location_id=location_id, current_user=current_user, db=db)
    elif report_type == "staff":
        return await staff_analytics(location_id=location_id, current_user=current_user, db=db)
    else:
        return await analytics_overview(location_id=location_id, current_user=current_user, db=db)


# ── AI Agent Managed Endpoints (Track 6: Intelligence) ──

@router.get("/agents/track6/franchise/bi", response_model=APIResponse)
async def franchise_bi_agent(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles([UserRole.FRANCHISE_OWNER, UserRole.REGIONAL_MANAGER, UserRole.SUPER_ADMIN])),
):
    """Bridge to franchise_bi_dashboard_handler."""
    return await franchise_bi_dashboard_handler(db, user)


@router.get("/agents/track6/training/roi", response_model=APIResponse)
async def ai_training_roi_agent(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles([UserRole.FRANCHISE_OWNER, UserRole.REGIONAL_MANAGER, UserRole.SUPER_ADMIN])),
):
    """Bridge to training_roi_handler (AI version)."""
    return await ai_training_roi_handler(db, user)


@router.get("/agents/track6/franchise/compare", response_model=APIResponse)
async def franchise_compare_agent(
    city: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles([UserRole.FRANCHISE_OWNER, UserRole.REGIONAL_MANAGER, UserRole.SUPER_ADMIN])),
):
    """Bridge to franchise_live_compare_handler."""
    return await franchise_live_compare_handler(city, db, user)


@router.get("/agents/track6/customer/ltv", response_model=APIResponse)
async def customer_ltv_agent(
    customer_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles([UserRole.SALON_MANAGER, UserRole.FRANCHISE_OWNER, UserRole.SUPER_ADMIN])),
):
    """Bridge to customer_ltv_model_handler."""
    return await customer_ltv_model_handler(customer_id, db, user)


@router.get("/agents/track6/skills/forecast", response_model=APIResponse)
async def skill_gap_forecast_agent(
    location_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles([UserRole.SALON_MANAGER, UserRole.REGIONAL_MANAGER, UserRole.SUPER_ADMIN])),
):
    """Bridge to skill_gap_forecast_handler."""
    return await ai_skill_gap_forecast_handler(location_id, db, user)

