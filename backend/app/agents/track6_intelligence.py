"""Track 6: Business Intelligence — 10 agents for franchise analytics, career
pathing, portfolio optimization, and predictive business health (PS-06.01
through PS-06.10)."""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Query
from sqlalchemy import select, func, case, and_, or_, literal, distinct, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, enum_val
from app.dependencies import get_current_user, require_role
from app.models import (
    User, Location, StaffProfile, SkillLevel, CustomerProfile,
    Service, SOP, Booking, BookingStatus, ServiceSession, SessionStatus,
    SmartQueueEntry, QueueStatus, CustomerFeedback, Sentiment,
    QualityAssessment, SkillAssessment, TrainingRecord, Notification,
    TrendSignal, TrendTrajectory,
)
from app.models.loyalty import LoyaltyProgram
from app.models.inventory import InventoryItem, InventoryUsageLog
from app.models.scheduling import StaffSchedule
from app.schemas.common import APIResponse
from app.agents import AgentAction, register_agent


# ═══════════════════════════════════════════════════════════════════════════════
# 54. franchise_bi_dashboard (PS-06.01)
# ═══════════════════════════════════════════════════════════════════════════════

async def franchise_bi_dashboard_handler(
    location_ids: Optional[str] = Query(None, description="Comma-separated location IDs"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "franchise_owner", "regional_manager", "super_admin"])),
):
    """Per-location franchise BI metrics: revenue, margins, utilization, peaks."""
    now = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)

    # Determine locations to analyze
    if location_ids:
        loc_id_list = [lid.strip() for lid in location_ids.split(",")]
        locations_result = await db.execute(
            select(Location).where(Location.id.in_(loc_id_list), Location.is_deleted == False)
        )
    else:
        locations_result = await db.execute(
            select(Location).where(Location.is_deleted == False, Location.is_active == True)
        )
    locations = locations_result.scalars().all()

    if not locations:
        raise HTTPException(status_code=404, detail="No locations found")

    dashboard = []
    for loc in locations:
        # Revenue in last 30 days
        rev_result = await db.execute(
            select(func.sum(Booking.final_price)).where(
                Booking.location_id == loc.id,
                Booking.status == BookingStatus.COMPLETED,
                Booking.actual_end_at >= thirty_days_ago,
            )
        )
        revenue_30d = float(rev_result.scalar() or 0)

        # Total completed services for cost calc
        svc_count_result = await db.execute(
            select(func.count(Booking.id)).where(
                Booking.location_id == loc.id,
                Booking.status == BookingStatus.COMPLETED,
                Booking.actual_end_at >= thirty_days_ago,
            )
        )
        total_services = svc_count_result.scalar() or 0

        # Cost per service = total product cost / services
        product_cost_result = await db.execute(
            select(func.sum(InventoryUsageLog.quantity_used * InventoryItem.cost_per_unit))
            .join(InventoryItem, InventoryItem.id == InventoryUsageLog.inventory_item_id)
            .where(
                InventoryItem.location_id == loc.id,
                InventoryUsageLog.created_at >= thirty_days_ago,
            )
        )
        total_product_cost = float(product_cost_result.scalar() or 0)
        cost_per_service = round(total_product_cost / max(total_services, 1), 2)

        # Margin by category
        margin_result = await db.execute(
            select(
                Service.category,
                func.sum(Booking.final_price).label("cat_revenue"),
                func.count(Booking.id).label("cat_count"),
            )
            .join(Service, Service.id == Booking.service_id)
            .where(
                Booking.location_id == loc.id,
                Booking.status == BookingStatus.COMPLETED,
                Booking.actual_end_at >= thirty_days_ago,
            )
            .group_by(Service.category)
            .order_by(func.sum(Booking.final_price).desc())
        )
        margin_by_category = []
        for row in margin_result.all():
            cat_rev = float(row.cat_revenue or 0)
            # Estimate margin at 60% for services (labor-based)
            estimated_margin_pct = 60.0
            margin_by_category.append({
                "category": row.category or "Uncategorized",
                "revenue": round(cat_rev, 2),
                "bookings": row.cat_count,
                "margin_pct": estimated_margin_pct,
            })

        # Revenue per stylist hour
        stylist_count_result = await db.execute(
            select(func.count(StaffProfile.id)).where(
                StaffProfile.location_id == loc.id,
                StaffProfile.is_available == True,
            )
        )
        stylist_count = stylist_count_result.scalar() or 1
        working_hours_30d = stylist_count * 8 * 26  # 8 hrs/day, 26 working days
        revenue_per_stylist_hour = round(revenue_30d / max(working_hours_30d, 1), 2)

        # Peak day of week (0=Mon, 6=Sun)
        peak_day_result = await db.execute(
            select(
                func.extract("dow", Booking.scheduled_at).label("dow"),
                func.count(Booking.id).label("cnt"),
            )
            .where(
                Booking.location_id == loc.id,
                Booking.status == BookingStatus.COMPLETED,
                Booking.scheduled_at >= thirty_days_ago,
            )
            .group_by(func.extract("dow", Booking.scheduled_at))
            .order_by(func.count(Booking.id).desc())
            .limit(1)
        )
        peak_day_row = peak_day_result.first()
        day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        peak_day = day_names[int(peak_day_row.dow)] if peak_day_row else "N/A"

        # Peak time
        peak_time_result = await db.execute(
            select(
                func.extract("hour", Booking.scheduled_at).label("hr"),
                func.count(Booking.id).label("cnt"),
            )
            .where(
                Booking.location_id == loc.id,
                Booking.status == BookingStatus.COMPLETED,
                Booking.scheduled_at >= thirty_days_ago,
            )
            .group_by(func.extract("hour", Booking.scheduled_at))
            .order_by(func.count(Booking.id).desc())
            .limit(1)
        )
        peak_time_row = peak_time_result.first()
        peak_time = f"{int(peak_time_row.hr):02d}:00" if peak_time_row else "N/A"

        # Utilization: actual bookings / total capacity (stylists * 8 slots/day * 26 days)
        capacity = stylist_count * 8 * 26
        utilization_pct = round(total_services / max(capacity, 1) * 100, 1)

        dashboard.append({
            "location_id": loc.id,
            "location": loc.name,
            "city": loc.city,
            "revenue_30d": round(revenue_30d, 2),
            "cost_per_service": cost_per_service,
            "margin_by_category": margin_by_category,
            "revenue_per_stylist_hour": revenue_per_stylist_hour,
            "peak_day": peak_day,
            "peak_time": peak_time,
            "utilization_pct": utilization_pct,
            "total_services_30d": total_services,
            "stylist_count": stylist_count,
        })

    return APIResponse(success=True, data=dashboard)


agent_franchise_bi = register_agent(AgentAction(
    name="franchise_bi_dashboard",
    description="Franchise-wide business intelligence dashboard with per-location revenue, margins, and utilization",
    track="intelligence",
    feature="franchise_bi",
    method="get",
    path="/agents/track6/franchise/dashboard",
    handler=franchise_bi_dashboard_handler,
    roles=["salon_manager", "franchise_owner", "regional_manager", "super_admin"],
    ps_codes=["PS-06.01"],
))


# ═══════════════════════════════════════════════════════════════════════════════
# 55. training_roi (PS-06.02)
# ═══════════════════════════════════════════════════════════════════════════════

async def training_roi_handler(
    staff_id: Optional[str] = Query(None),
    training_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "franchise_owner", "regional_manager", "super_admin"])),
):
    """Compute training ROI: revenue/quality before vs after, payback period."""
    query = select(TrainingRecord)
    if staff_id:
        query = query.where(TrainingRecord.staff_id == staff_id)
    if training_id:
        query = query.where(TrainingRecord.id == training_id)

    query = query.order_by(TrainingRecord.start_date.desc())
    result = await db.execute(query)
    trainings = result.scalars().all()

    if not trainings:
        raise HTTPException(status_code=404, detail="No training records found")

    roi_data = []
    for tr in trainings:
        cost = float(tr.cost_to_company or 0)
        rev_before = float(tr.revenue_before or 0)
        rev_after = float(tr.revenue_after or 0)
        quality_before = float(tr.quality_score_before or 0)
        quality_after = float(tr.quality_score_after or 0)

        revenue_delta = rev_after - rev_before
        quality_delta = quality_after - quality_before

        # ROI = (revenue increase - cost) / cost * 100
        roi_pct = round((revenue_delta - cost) / max(cost, 1) * 100, 1) if cost > 0 else 0.0

        # Payback period: cost / monthly revenue increase * 30 days
        monthly_rev_increase = revenue_delta  # revenue_before/after are monthly figures
        payback_days = int(cost / max(monthly_rev_increase, 1) * 30) if monthly_rev_increase > 0 else None

        roi_data.append({
            "training_id": tr.id,
            "training_name": tr.training_name,
            "staff_id": tr.staff_id,
            "training_type": enum_val(tr.training_type) if tr.training_type else None,
            "service_category": tr.service_category,
            "cost": cost,
            "revenue_before": rev_before,
            "revenue_after": rev_after,
            "revenue_delta": round(revenue_delta, 2),
            "quality_before": quality_before,
            "quality_after": quality_after,
            "quality_delta": round(quality_delta, 2),
            "roi_pct": roi_pct,
            "payback_period_days": payback_days,
            "passed": tr.passed,
            "start_date": str(tr.start_date) if tr.start_date else None,
            "end_date": str(tr.end_date) if tr.end_date else None,
        })

    return APIResponse(success=True, data=roi_data)


agent_training_roi = register_agent(AgentAction(
    name="training_roi",
    description="Compute training ROI with revenue/quality deltas and payback periods",
    track="intelligence",
    feature="training_roi",
    method="get",
    path="/agents/track6/training/roi",
    handler=training_roi_handler,
    roles=["salon_manager", "franchise_owner", "regional_manager", "super_admin"],
    ps_codes=["PS-06.02"],
))


# ═══════════════════════════════════════════════════════════════════════════════
# 56. unified_intelligence (PS-06.03)
# ═══════════════════════════════════════════════════════════════════════════════

async def unified_intelligence_handler(
    staff_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "franchise_owner", "regional_manager", "super_admin"])),
):
    """Unified view joining skills, revenue, and customer outcome data."""
    now = datetime.now(timezone.utc)
    ninety_days_ago = now - timedelta(days=90)

    # Verify staff
    staff_result = await db.execute(
        select(StaffProfile).where(StaffProfile.id == staff_id)
    )
    staff = staff_result.scalar_one_or_none()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    skill_level = enum_val(staff.skill_level) if staff.skill_level else "Unknown"

    # Total revenue
    rev_result = await db.execute(
        select(func.sum(Booking.final_price)).where(
            Booking.stylist_id == staff_id,
            Booking.status == BookingStatus.COMPLETED,
            Booking.actual_end_at >= ninety_days_ago,
        )
    )
    total_revenue = float(rev_result.scalar() or 0)

    # Unique customers served
    cust_count_result = await db.execute(
        select(func.count(distinct(Booking.customer_id))).where(
            Booking.stylist_id == staff_id,
            Booking.status == BookingStatus.COMPLETED,
            Booking.actual_end_at >= ninety_days_ago,
        )
    )
    unique_customers = cust_count_result.scalar() or 1
    avg_revenue_per_customer = round(total_revenue / max(unique_customers, 1), 2)

    # Quality score average
    quality_result = await db.execute(
        select(func.avg(QualityAssessment.overall_score)).where(
            QualityAssessment.stylist_id == staff_id,
            QualityAssessment.created_at >= ninety_days_ago,
        )
    )
    quality_score_avg = round(float(quality_result.scalar() or 0), 2)

    # Customer satisfaction average
    sat_result = await db.execute(
        select(func.avg(CustomerFeedback.overall_rating)).where(
            CustomerFeedback.stylist_id == staff_id,
            CustomerFeedback.created_at >= ninety_days_ago,
        )
    )
    customer_satisfaction_avg = round(float(sat_result.scalar() or 0), 2)

    # Correlation insight: compare revenue across skill levels
    skill_rev_result = await db.execute(
        select(
            StaffProfile.skill_level,
            func.avg(Booking.final_price).label("avg_rev"),
        )
        .join(Booking, Booking.stylist_id == StaffProfile.id)
        .where(
            Booking.status == BookingStatus.COMPLETED,
            Booking.actual_end_at >= ninety_days_ago,
            StaffProfile.skill_level != None,
        )
        .group_by(StaffProfile.skill_level)
    )
    skill_revenues = {
        enum_val(row.skill_level): float(row.avg_rev or 0)
        for row in skill_rev_result.all()
    }

    l1_rev = skill_revenues.get("L1", 0)
    l3_rev = skill_revenues.get("L3", 0)
    if l1_rev > 0:
        pct_more = round((l3_rev - l1_rev) / l1_rev * 100, 1)
        correlation_insight = f"L3 stylists generate {pct_more}% more revenue per booking than L1 stylists"
    else:
        correlation_insight = "Insufficient data for cross-skill revenue comparison"

    return APIResponse(
        success=True,
        data={
            "staff_id": staff_id,
            "skill_level": skill_level,
            "total_revenue_90d": round(total_revenue, 2),
            "unique_customers_90d": unique_customers,
            "avg_revenue_per_customer": avg_revenue_per_customer,
            "quality_score_avg": quality_score_avg,
            "customer_satisfaction_avg": customer_satisfaction_avg,
            "correlation_insight": correlation_insight,
            "skill_level_revenue_comparison": skill_revenues,
        },
    )


agent_unified_intel = register_agent(AgentAction(
    name="unified_intelligence",
    description="Unified intelligence view joining skill data, revenue, and customer outcomes for a stylist",
    track="intelligence",
    feature="unified",
    method="get",
    path="/agents/track6/unified/intelligence",
    handler=unified_intelligence_handler,
    roles=["salon_manager", "franchise_owner", "regional_manager", "super_admin"],
    ps_codes=["PS-06.03"],
))


# ═══════════════════════════════════════════════════════════════════════════════
# 57. franchise_live_compare (PS-06.04)
# ═══════════════════════════════════════════════════════════════════════════════

async def franchise_live_compare_handler(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["franchise_owner", "regional_manager", "super_admin"])),
):
    """All locations ranked by composite score across multiple dimensions."""
    now = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)
    sixty_days_ago = now - timedelta(days=60)

    locations_result = await db.execute(
        select(Location).where(Location.is_deleted == False, Location.is_active == True)
    )
    locations = locations_result.scalars().all()

    if not locations:
        return APIResponse(success=True, data=[])

    location_metrics = []
    for loc in locations:
        # Revenue 30d
        rev_result = await db.execute(
            select(func.sum(Booking.final_price)).where(
                Booking.location_id == loc.id,
                Booking.status == BookingStatus.COMPLETED,
                Booking.actual_end_at >= thirty_days_ago,
            )
        )
        revenue = float(rev_result.scalar() or 0)

        # Revenue previous 30d (for trend)
        prev_rev_result = await db.execute(
            select(func.sum(Booking.final_price)).where(
                Booking.location_id == loc.id,
                Booking.status == BookingStatus.COMPLETED,
                Booking.actual_end_at >= sixty_days_ago,
                Booking.actual_end_at < thirty_days_ago,
            )
        )
        prev_revenue = float(prev_rev_result.scalar() or 0)

        # Quality average
        qual_result = await db.execute(
            select(func.avg(QualityAssessment.overall_score)).where(
                QualityAssessment.location_id == loc.id,
                QualityAssessment.created_at >= thirty_days_ago,
            )
        )
        quality_avg = float(qual_result.scalar() or 0)

        # Customer satisfaction
        sat_result = await db.execute(
            select(func.avg(CustomerFeedback.overall_rating)).where(
                CustomerFeedback.location_id == loc.id,
                CustomerFeedback.created_at >= thirty_days_ago,
            )
        )
        satisfaction_avg = float(sat_result.scalar() or 0)

        # Utilization
        svc_count_result = await db.execute(
            select(func.count(Booking.id)).where(
                Booking.location_id == loc.id,
                Booking.status == BookingStatus.COMPLETED,
                Booking.actual_end_at >= thirty_days_ago,
            )
        )
        svc_count = svc_count_result.scalar() or 0

        stylist_count_result = await db.execute(
            select(func.count(StaffProfile.id)).where(
                StaffProfile.location_id == loc.id,
                StaffProfile.is_available == True,
            )
        )
        stylist_count = stylist_count_result.scalar() or 1
        capacity = stylist_count * 8 * 26
        utilization = round(svc_count / max(capacity, 1) * 100, 1)

        # Trend
        if prev_revenue > 0:
            rev_change = (revenue - prev_revenue) / prev_revenue * 100
            if rev_change > 5:
                trend = "improving"
            elif rev_change < -5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"

        location_metrics.append({
            "location_id": loc.id,
            "location": loc.name,
            "city": loc.city,
            "revenue": revenue,
            "quality": quality_avg,
            "satisfaction": satisfaction_avg,
            "utilization": utilization,
            "trend": trend,
        })

    # Rank each dimension
    def rank_by(items, key, reverse=True):
        sorted_items = sorted(items, key=lambda x: x[key], reverse=reverse)
        for rank, item in enumerate(sorted_items, 1):
            item[f"{key}_rank"] = rank

    rank_by(location_metrics, "revenue")
    rank_by(location_metrics, "quality")
    rank_by(location_metrics, "satisfaction")
    rank_by(location_metrics, "utilization")

    # Compute composite rank (lower = better)
    for m in location_metrics:
        m["composite_score"] = (
            m["revenue_rank"] + m["quality_rank"] +
            m["satisfaction_rank"] + m["utilization_rank"]
        )

    location_metrics.sort(key=lambda x: x["composite_score"])
    for rank, m in enumerate(location_metrics, 1):
        m["composite_rank"] = rank
        m["revenue_rank"] = m.pop("revenue_rank")
        m["quality_rank"] = m.pop("quality_rank")
        m["customer_satisfaction_rank"] = m.pop("satisfaction_rank")
        m["utilization_rank"] = m.pop("utilization_rank")
        # Clean up intermediate keys
        m["revenue_30d"] = round(m.pop("revenue"), 2)
        m["quality_avg"] = round(m.pop("quality"), 2)
        m["satisfaction_avg"] = round(m.pop("satisfaction"), 2)
        m["utilization_pct"] = m.pop("utilization")

    # Highlight top 3 and bottom 3
    top_3 = [m["location"] for m in location_metrics[:3]]
    bottom_3 = [m["location"] for m in location_metrics[-3:]] if len(location_metrics) >= 3 else []

    return APIResponse(
        success=True,
        data={
            "rankings": location_metrics,
            "top_3_locations": top_3,
            "bottom_3_locations": bottom_3,
            "total_locations": len(location_metrics),
        },
    )


agent_live_compare = register_agent(AgentAction(
    name="franchise_live_compare",
    description="All franchise locations ranked by composite score across revenue, quality, satisfaction, and utilization",
    track="intelligence",
    feature="franchise_compare",
    method="get",
    path="/agents/track6/franchise/compare",
    handler=franchise_live_compare_handler,
    roles=["franchise_owner", "regional_manager", "super_admin"],
    ps_codes=["PS-06.04"],
))


# ═══════════════════════════════════════════════════════════════════════════════
# 58. customer_ltv_model (PS-06.05)
# ═══════════════════════════════════════════════════════════════════════════════

async def customer_ltv_model_handler(
    customer_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "franchise_owner", "regional_manager", "super_admin"])),
):
    """Customer LTV model: individual detail or segment summary."""
    now = datetime.now(timezone.utc)
    sixty_days_ago = now - timedelta(days=60)

    if customer_id:
        # Individual customer LTV
        cp_result = await db.execute(
            select(CustomerProfile).where(CustomerProfile.id == customer_id)
        )
        customer = cp_result.scalar_one_or_none()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        ltv = float(customer.lifetime_value or 0)
        total_visits = customer.total_visits or 0

        # Determine segment based on LTV
        if ltv >= 50000:
            segment = "platinum"
        elif ltv >= 20000:
            segment = "gold"
        elif ltv >= 5000:
            segment = "silver"
        else:
            segment = "bronze"

        # Churn risk: days since last visit
        last_visit = customer.last_visit_date
        if last_visit:
            if isinstance(last_visit, str):
                from datetime import date
                last_visit_date = date.fromisoformat(last_visit)
            else:
                last_visit_date = last_visit
            days_since = (now.date() - last_visit_date).days
            if days_since > 90:
                churn_risk = "high"
            elif days_since > 45:
                churn_risk = "medium"
            else:
                churn_risk = "low"
        else:
            churn_risk = "high"

        # Predicted next visit based on average interval
        booking_dates_result = await db.execute(
            select(Booking.scheduled_at).where(
                Booking.customer_id == customer_id,
                Booking.status == BookingStatus.COMPLETED,
            ).order_by(Booking.scheduled_at.desc()).limit(10)
        )
        dates = [row[0] for row in booking_dates_result.all()]
        if len(dates) >= 2:
            intervals = []
            for i in range(len(dates) - 1):
                d1 = dates[i] if isinstance(dates[i], datetime) else datetime.fromisoformat(str(dates[i]))
                d2 = dates[i + 1] if isinstance(dates[i + 1], datetime) else datetime.fromisoformat(str(dates[i + 1]))
                interval = abs((d1 - d2).days)
                if interval > 0:
                    intervals.append(interval)
            avg_interval = int(sum(intervals) / len(intervals)) if intervals else 30
            last_date = dates[0] if isinstance(dates[0], datetime) else datetime.fromisoformat(str(dates[0]))
            predicted_next = last_date + timedelta(days=avg_interval)
            predicted_next_visit = str(predicted_next.date())
        else:
            predicted_next_visit = None

        # Top services
        top_svc_result = await db.execute(
            select(Service.name, func.count(Booking.id).label("cnt"))
            .join(Booking, Booking.service_id == Service.id)
            .where(
                Booking.customer_id == customer_id,
                Booking.status == BookingStatus.COMPLETED,
            )
            .group_by(Service.name)
            .order_by(func.count(Booking.id).desc())
            .limit(5)
        )
        top_services = [row.name for row in top_svc_result.all()]

        return APIResponse(
            success=True,
            data={
                "customer_id": customer_id,
                "lifetime_value": round(ltv, 2),
                "total_visits": total_visits,
                "segment": segment,
                "churn_risk": churn_risk,
                "predicted_next_visit": predicted_next_visit,
                "top_services": top_services,
            },
        )
    else:
        # Segment summary
        segments = []
        thresholds = [
            ("platinum", 50000, None),
            ("gold", 20000, 50000),
            ("silver", 5000, 20000),
            ("bronze", 0, 5000),
        ]
        for seg_name, low, high in thresholds:
            query = select(
                func.count(CustomerProfile.id).label("count"),
                func.avg(CustomerProfile.lifetime_value).label("avg_ltv"),
                func.avg(CustomerProfile.total_visits).label("avg_visits"),
            ).where(CustomerProfile.lifetime_value >= low)
            if high is not None:
                query = query.where(CustomerProfile.lifetime_value < high)

            seg_result = await db.execute(query)
            seg_row = seg_result.first()

            count = seg_row.count or 0
            avg_ltv = round(float(seg_row.avg_ltv or 0), 2)
            avg_visits = round(float(seg_row.avg_visits or 0), 1)

            # Churn rate: proportion who haven't visited in 60+ days
            if count > 0:
                churned_result = await db.execute(
                    select(func.count(CustomerProfile.id)).where(
                        CustomerProfile.lifetime_value >= low,
                        CustomerProfile.lifetime_value < high if high else literal(True),
                        or_(
                            CustomerProfile.last_visit_date == None,
                            CustomerProfile.last_visit_date < str(sixty_days_ago.date()),
                        ),
                    )
                )
                churned = churned_result.scalar() or 0
                churn_rate = round(churned / max(count, 1) * 100, 1)
            else:
                churn_rate = 0.0

            # Top services for this segment
            top_svc_result = await db.execute(
                select(Service.name, func.count(Booking.id).label("cnt"))
                .join(Booking, Booking.service_id == Service.id)
                .join(CustomerProfile, CustomerProfile.id == Booking.customer_id)
                .where(
                    Booking.status == BookingStatus.COMPLETED,
                    CustomerProfile.lifetime_value >= low,
                    CustomerProfile.lifetime_value < high if high else literal(True),
                )
                .group_by(Service.name)
                .order_by(func.count(Booking.id).desc())
                .limit(3)
            )
            top_services = [row.name for row in top_svc_result.all()]

            segments.append({
                "segment": seg_name,
                "count": count,
                "avg_ltv": avg_ltv,
                "avg_visits": avg_visits,
                "churn_rate": churn_rate,
                "top_services": top_services,
            })

        return APIResponse(success=True, data=segments)


agent_customer_ltv = register_agent(AgentAction(
    name="customer_ltv_model",
    description="Customer lifetime value model with individual LTV/churn or segment summary analysis",
    track="intelligence",
    feature="customer_ltv",
    method="get",
    path="/agents/track6/customer/ltv",
    handler=customer_ltv_model_handler,
    roles=["salon_manager", "franchise_owner", "regional_manager", "super_admin"],
    ps_codes=["PS-06.05"],
))


# ═══════════════════════════════════════════════════════════════════════════════
# 59. skill_gap_forecast (PS-06.06)
# ═══════════════════════════════════════════════════════════════════════════════

async def skill_gap_forecast_handler(
    service_category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "franchise_owner", "regional_manager", "super_admin"])),
):
    """Map current skill inventory against service demand and identify gaps."""
    now = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)
    sixty_days_ago = now - timedelta(days=60)

    # Get all service categories
    cat_query = select(distinct(Service.category)).where(
        Service.is_active == True, Service.category != None
    )
    if service_category:
        cat_query = cat_query.where(Service.category.ilike(f"%{service_category}%"))
    cat_result = await db.execute(cat_query)
    categories = [row[0] for row in cat_result.all()]

    gaps = []
    for cat in categories:
        # Current demand: bookings in last 30 days for this category
        demand_30d_result = await db.execute(
            select(func.count(Booking.id))
            .join(Service, Service.id == Booking.service_id)
            .where(
                Service.category == cat,
                Booking.status == BookingStatus.COMPLETED,
                Booking.actual_end_at >= thirty_days_ago,
            )
        )
        demand_30d = demand_30d_result.scalar() or 0

        # Previous 30 days demand for trend
        demand_prev_result = await db.execute(
            select(func.count(Booking.id))
            .join(Service, Service.id == Booking.service_id)
            .where(
                Service.category == cat,
                Booking.status == BookingStatus.COMPLETED,
                Booking.actual_end_at >= sixty_days_ago,
                Booking.actual_end_at < thirty_days_ago,
            )
        )
        demand_prev = demand_prev_result.scalar() or 0

        if demand_prev > 0:
            demand_change = (demand_30d - demand_prev) / demand_prev * 100
            if demand_change > 10:
                demand_trend = "growing"
            elif demand_change < -10:
                demand_trend = "declining"
            else:
                demand_trend = "stable"
        else:
            demand_trend = "new" if demand_30d > 0 else "no_data"

        # Qualified stylists: those with skill assessments in this category
        qualified_result = await db.execute(
            select(func.count(distinct(SkillAssessment.staff_id))).where(
                SkillAssessment.service_category == cat,
                SkillAssessment.score >= 7.0,
            )
        )
        qualified_count = qualified_result.scalar() or 0

        # Required stylists estimate: demand / 8 bookings per day / 26 days + buffer
        daily_demand = demand_30d / 26
        required_stylists = max(1, int(daily_demand / 6) + 1)  # 6 services/stylist/day
        gap_count = max(0, required_stylists - qualified_count)

        # Branches with gap
        branches_result = await db.execute(
            select(Location.name)
            .where(
                Location.is_active == True,
                Location.is_deleted == False,
                ~Location.id.in_(
                    select(distinct(StaffProfile.location_id))
                    .join(SkillAssessment, SkillAssessment.staff_id == StaffProfile.id)
                    .where(
                        SkillAssessment.service_category == cat,
                        SkillAssessment.score >= 7.0,
                    )
                ),
            )
        )
        branches_with_gap = [row[0] for row in branches_result.all()]

        # Training recommendation
        training_rec = None
        if gap_count > 0:
            training_result = await db.execute(
                select(TrainingRecord.training_name).where(
                    TrainingRecord.service_category == cat,
                    TrainingRecord.passed == True,
                ).order_by(TrainingRecord.created_at.desc()).limit(1)
            )
            existing_training = training_result.scalar_one_or_none()
            training_rec = existing_training or f"Recommended: {cat} skill development program"

        # Estimated readiness: assume 4-8 weeks for training
        estimated_readiness = str((now + timedelta(weeks=6)).date()) if gap_count > 0 else None

        gaps.append({
            "service_category": cat,
            "demand_30d": demand_30d,
            "demand_trend": demand_trend,
            "qualified_stylists_count": qualified_count,
            "required_stylists_estimate": required_stylists,
            "gap_count": gap_count,
            "branches_with_gap": branches_with_gap[:5],
            "training_recommendation": training_rec,
            "estimated_readiness_date": estimated_readiness,
        })

    # Sort by gap severity
    gaps.sort(key=lambda x: x["gap_count"], reverse=True)

    return APIResponse(success=True, data=gaps)


agent_skill_gap = register_agent(AgentAction(
    name="skill_gap_forecast",
    description="Map skill inventory against service demand to identify staffing gaps and training needs",
    track="intelligence",
    feature="skill_gap",
    method="get",
    path="/agents/track6/skills/gap-forecast",
    handler=skill_gap_forecast_handler,
    roles=["salon_manager", "franchise_owner", "regional_manager", "super_admin"],
    ps_codes=["PS-06.06"],
))


# ═══════════════════════════════════════════════════════════════════════════════
# 60. product_usage_intelligence (PS-06.07)
# ═══════════════════════════════════════════════════════════════════════════════

async def product_usage_intelligence_handler(
    location_id: Optional[str] = Query(None),
    service_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "franchise_owner", "regional_manager", "super_admin"])),
):
    """Correlate product usage with quality scores; identify waste and best practices."""
    now = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)

    # Base query for usage logs
    usage_query = (
        select(
            InventoryItem.location_id,
            func.avg(InventoryUsageLog.quantity_used).label("avg_usage"),
            func.avg(InventoryUsageLog.quality_score_of_service).label("avg_quality"),
            func.count(InventoryUsageLog.id).label("usage_count"),
            func.sum(InventoryUsageLog.quantity_used).label("total_usage"),
        )
        .join(InventoryItem, InventoryItem.id == InventoryUsageLog.inventory_item_id)
        .where(InventoryUsageLog.created_at >= thirty_days_ago)
    )

    if location_id:
        usage_query = usage_query.where(InventoryItem.location_id == location_id)

    if service_id:
        usage_query = usage_query.where(
            InventoryUsageLog.session_id.in_(
                select(ServiceSession.id)
                .join(Booking, Booking.id == ServiceSession.booking_id)
                .where(Booking.service_id == service_id)
            )
        )

    usage_query = usage_query.group_by(InventoryItem.location_id)
    usage_result = await db.execute(usage_query)
    rows = usage_result.all()

    if not rows:
        return APIResponse(
            success=True,
            data={
                "avg_product_usage": 0,
                "quality_score_correlation": "insufficient_data",
                "waste_indicator": "unknown",
                "best_practice_locations": [],
                "training_needed_locations": [],
            },
        )

    # Process per-location data
    location_data = []
    all_usages = []
    all_qualities = []

    for row in rows:
        avg_u = float(row.avg_usage or 0)
        avg_q = float(row.avg_quality or 0)
        all_usages.append(avg_u)
        all_qualities.append(avg_q)
        location_data.append({
            "location_id": row.location_id,
            "avg_usage": round(avg_u, 2),
            "avg_quality": round(avg_q, 2),
            "usage_count": row.usage_count,
            "total_usage": round(float(row.total_usage or 0), 2),
        })

    global_avg_usage = round(sum(all_usages) / len(all_usages), 2) if all_usages else 0
    global_avg_quality = round(sum(all_qualities) / len(all_qualities), 2) if all_qualities else 0

    # Simple correlation: compare locations with above-avg usage to below-avg usage quality
    above_avg_quality = [d["avg_quality"] for d in location_data if d["avg_usage"] > global_avg_usage]
    below_avg_quality = [d["avg_quality"] for d in location_data if d["avg_usage"] <= global_avg_usage]

    above_mean = sum(above_avg_quality) / len(above_avg_quality) if above_avg_quality else 0
    below_mean = sum(below_avg_quality) / len(below_avg_quality) if below_avg_quality else 0

    if above_mean > below_mean + 0.5:
        correlation = "positive — higher product usage correlates with higher quality"
    elif below_mean > above_mean + 0.5:
        correlation = "negative — lower product usage achieves higher quality (potential waste elsewhere)"
    else:
        correlation = "neutral — product usage has minimal impact on quality scores"

    # Waste indicator
    high_usage_low_quality = [
        d for d in location_data
        if d["avg_usage"] > global_avg_usage * 1.3 and d["avg_quality"] < global_avg_quality
    ]
    waste_indicator = "high" if high_usage_low_quality else "low"

    # Best practice locations: high quality, moderate usage
    best_practice = sorted(
        [d for d in location_data if d["avg_quality"] >= global_avg_quality],
        key=lambda x: x["avg_quality"],
        reverse=True,
    )[:3]
    best_practice_ids = [d["location_id"] for d in best_practice]

    # Resolve location names
    if best_practice_ids:
        bp_names_result = await db.execute(
            select(Location.id, Location.name).where(Location.id.in_(best_practice_ids))
        )
        bp_names = {row.id: row.name for row in bp_names_result.all()}
        best_practice_locations = [bp_names.get(lid, lid) for lid in best_practice_ids]
    else:
        best_practice_locations = []

    # Training needed: high waste locations
    training_ids = [d["location_id"] for d in high_usage_low_quality]
    if training_ids:
        tn_names_result = await db.execute(
            select(Location.id, Location.name).where(Location.id.in_(training_ids))
        )
        tn_names = {row.id: row.name for row in tn_names_result.all()}
        training_needed_locations = [tn_names.get(lid, lid) for lid in training_ids]
    else:
        training_needed_locations = []

    return APIResponse(
        success=True,
        data={
            "avg_product_usage": global_avg_usage,
            "avg_quality_score": global_avg_quality,
            "quality_score_correlation": correlation,
            "waste_indicator": waste_indicator,
            "best_practice_locations": best_practice_locations,
            "training_needed_locations": training_needed_locations,
            "location_breakdown": location_data,
        },
    )


agent_product_usage = register_agent(AgentAction(
    name="product_usage_intelligence",
    description="Correlate product usage with quality scores to identify waste and best practices",
    track="intelligence",
    feature="product_usage",
    method="get",
    path="/agents/track6/product/usage-intelligence",
    handler=product_usage_intelligence_handler,
    roles=["salon_manager", "franchise_owner", "regional_manager", "super_admin"],
    ps_codes=["PS-06.07"],
))


# ═══════════════════════════════════════════════════════════════════════════════
# 61. branch_health_predictor (PS-06.08)
# ═══════════════════════════════════════════════════════════════════════════════

async def branch_health_predictor_handler(
    location_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "franchise_owner", "regional_manager", "super_admin"])),
):
    """Compute branch health score from multiple leading indicators and predict trajectory."""
    now = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)
    sixty_days_ago = now - timedelta(days=60)
    ninety_days_ago = now - timedelta(days=90)

    # Verify location
    loc_result = await db.execute(
        select(Location).where(Location.id == location_id)
    )
    location = loc_result.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    indicators = []

    # 1. Rebooking rate trend
    # Current 30d rebooking
    unique_current = await db.execute(
        select(func.count(distinct(Booking.customer_id))).where(
            Booking.location_id == location_id,
            Booking.status == BookingStatus.COMPLETED,
            Booking.actual_end_at >= thirty_days_ago,
        )
    )
    current_customers = unique_current.scalar() or 0

    repeat_current = await db.execute(
        select(func.count(distinct(Booking.customer_id))).where(
            Booking.location_id == location_id,
            Booking.status == BookingStatus.COMPLETED,
            Booking.actual_end_at >= thirty_days_ago,
            Booking.customer_id.in_(
                select(Booking.customer_id).where(
                    Booking.location_id == location_id,
                    Booking.status == BookingStatus.COMPLETED,
                    Booking.actual_end_at >= sixty_days_ago,
                    Booking.actual_end_at < thirty_days_ago,
                )
            ),
        )
    )
    repeat_count = repeat_current.scalar() or 0

    # Previous period unique customers for the denominator
    unique_prev = await db.execute(
        select(func.count(distinct(Booking.customer_id))).where(
            Booking.location_id == location_id,
            Booking.status == BookingStatus.COMPLETED,
            Booking.actual_end_at >= sixty_days_ago,
            Booking.actual_end_at < thirty_days_ago,
        )
    )
    prev_customers = unique_prev.scalar() or 1

    rebooking_rate = round(repeat_count / max(prev_customers, 1) * 100, 1)
    rebooking_risk = "low" if rebooking_rate >= 40 else ("medium" if rebooking_rate >= 25 else "high")
    indicators.append({
        "indicator": "rebooking_rate",
        "current_value": rebooking_rate,
        "trend": "healthy" if rebooking_rate >= 40 else "concerning",
        "risk_level": rebooking_risk,
    })

    # 2. Complaint frequency trend
    complaints_current = await db.execute(
        select(func.count(CustomerFeedback.id)).where(
            CustomerFeedback.location_id == location_id,
            CustomerFeedback.sentiment == Sentiment.NEGATIVE,
            CustomerFeedback.created_at >= thirty_days_ago,
        )
    )
    complaints_30d = complaints_current.scalar() or 0

    complaints_prev = await db.execute(
        select(func.count(CustomerFeedback.id)).where(
            CustomerFeedback.location_id == location_id,
            CustomerFeedback.sentiment == Sentiment.NEGATIVE,
            CustomerFeedback.created_at >= sixty_days_ago,
            CustomerFeedback.created_at < thirty_days_ago,
        )
    )
    complaints_prev_30d = complaints_prev.scalar() or 0

    complaint_trend = "improving" if complaints_30d < complaints_prev_30d else (
        "stable" if complaints_30d == complaints_prev_30d else "worsening"
    )
    complaint_risk = "low" if complaints_30d <= 2 else ("medium" if complaints_30d <= 5 else "high")
    indicators.append({
        "indicator": "complaint_frequency",
        "current_value": complaints_30d,
        "previous_value": complaints_prev_30d,
        "trend": complaint_trend,
        "risk_level": complaint_risk,
    })

    # 3. Stylist stability (turnover in 90d)
    total_staff = await db.execute(
        select(func.count(StaffProfile.id)).where(
            StaffProfile.location_id == location_id,
        )
    )
    total_staff_count = total_staff.scalar() or 1

    # Stylists who joined recently (proxy for turnover)
    new_staff = await db.execute(
        select(func.count(StaffProfile.id)).where(
            StaffProfile.location_id == location_id,
            StaffProfile.created_at >= ninety_days_ago,
        )
    )
    new_staff_count = new_staff.scalar() or 0
    turnover_pct = round(new_staff_count / max(total_staff_count, 1) * 100, 1)
    stability_risk = "low" if turnover_pct < 15 else ("medium" if turnover_pct < 30 else "high")
    indicators.append({
        "indicator": "stylist_stability",
        "current_value": f"{100 - turnover_pct}% stable",
        "turnover_90d_pct": turnover_pct,
        "trend": "stable" if turnover_pct < 15 else "concerning",
        "risk_level": stability_risk,
    })

    # 4. Average ticket trend
    avg_ticket_current = await db.execute(
        select(func.avg(Booking.final_price)).where(
            Booking.location_id == location_id,
            Booking.status == BookingStatus.COMPLETED,
            Booking.actual_end_at >= thirty_days_ago,
        )
    )
    ticket_current = float(avg_ticket_current.scalar() or 0)

    avg_ticket_prev = await db.execute(
        select(func.avg(Booking.final_price)).where(
            Booking.location_id == location_id,
            Booking.status == BookingStatus.COMPLETED,
            Booking.actual_end_at >= sixty_days_ago,
            Booking.actual_end_at < thirty_days_ago,
        )
    )
    ticket_prev = float(avg_ticket_prev.scalar() or 0)

    ticket_change = round((ticket_current - ticket_prev) / max(ticket_prev, 1) * 100, 1) if ticket_prev else 0
    ticket_trend = "improving" if ticket_change > 5 else ("declining" if ticket_change < -5 else "stable")
    ticket_risk = "low" if ticket_change >= -5 else ("medium" if ticket_change >= -15 else "high")
    indicators.append({
        "indicator": "avg_ticket_value",
        "current_value": round(ticket_current, 2),
        "previous_value": round(ticket_prev, 2),
        "change_pct": ticket_change,
        "trend": ticket_trend,
        "risk_level": ticket_risk,
    })

    # 5. Quality score trend
    quality_current = await db.execute(
        select(func.avg(QualityAssessment.overall_score)).where(
            QualityAssessment.location_id == location_id,
            QualityAssessment.created_at >= thirty_days_ago,
        )
    )
    q_current = float(quality_current.scalar() or 0)

    quality_prev = await db.execute(
        select(func.avg(QualityAssessment.overall_score)).where(
            QualityAssessment.location_id == location_id,
            QualityAssessment.created_at >= sixty_days_ago,
            QualityAssessment.created_at < thirty_days_ago,
        )
    )
    q_prev = float(quality_prev.scalar() or 0)

    q_change = round(q_current - q_prev, 2)
    q_trend = "improving" if q_change > 0.2 else ("declining" if q_change < -0.2 else "stable")
    q_risk = "low" if q_current >= 8.0 else ("medium" if q_current >= 6.0 else "high")
    indicators.append({
        "indicator": "quality_score",
        "current_value": round(q_current, 2),
        "previous_value": round(q_prev, 2),
        "change": q_change,
        "trend": q_trend,
        "risk_level": q_risk,
    })

    # Compute health score (0-100)
    risk_weights = {"low": 0, "medium": 1, "high": 2}
    total_risk = sum(risk_weights.get(ind["risk_level"], 0) for ind in indicators)
    max_risk = 2 * len(indicators)
    health_score = round((1 - total_risk / max(max_risk, 1)) * 100, 1)

    if health_score >= 75:
        status = "healthy"
    elif health_score >= 50:
        status = "warning"
    else:
        status = "critical"

    # Predicted revenue change
    revenue_current = await db.execute(
        select(func.sum(Booking.final_price)).where(
            Booking.location_id == location_id,
            Booking.status == BookingStatus.COMPLETED,
            Booking.actual_end_at >= thirty_days_ago,
        )
    )
    rev_current = float(revenue_current.scalar() or 0)

    revenue_prev = await db.execute(
        select(func.sum(Booking.final_price)).where(
            Booking.location_id == location_id,
            Booking.status == BookingStatus.COMPLETED,
            Booking.actual_end_at >= sixty_days_ago,
            Booking.actual_end_at < thirty_days_ago,
        )
    )
    rev_prev = float(revenue_prev.scalar() or 0)
    rev_change_pct = round((rev_current - rev_prev) / max(rev_prev, 1) * 100, 1) if rev_prev else 0

    # Recommended actions
    recommended_actions = []
    for ind in indicators:
        if ind["risk_level"] == "high":
            if ind["indicator"] == "rebooking_rate":
                recommended_actions.append("Launch rebooking incentive campaign for existing customers")
            elif ind["indicator"] == "complaint_frequency":
                recommended_actions.append("Conduct quality audit and retrain low-performing stylists")
            elif ind["indicator"] == "stylist_stability":
                recommended_actions.append("Review compensation and work conditions to reduce turnover")
            elif ind["indicator"] == "avg_ticket_value":
                recommended_actions.append("Train staff on upselling and introduce premium service bundles")
            elif ind["indicator"] == "quality_score":
                recommended_actions.append("Schedule SOP refresher training and increase quality oversight")

    if not recommended_actions:
        recommended_actions.append("Maintain current performance; focus on incremental improvements")

    return APIResponse(
        success=True,
        data={
            "location_id": location_id,
            "location_name": location.name,
            "health_score": health_score,
            "status": status,
            "leading_indicators": indicators,
            "predicted_revenue_change_pct": rev_change_pct,
            "recommended_actions": recommended_actions,
        },
    )


agent_branch_health = register_agent(AgentAction(
    name="branch_health_predictor",
    description="Predictive branch health score from rebooking, complaints, turnover, ticket, and quality trends",
    track="intelligence",
    feature="branch_health",
    method="get",
    path="/agents/track6/branch/health",
    handler=branch_health_predictor_handler,
    roles=["salon_manager", "franchise_owner", "regional_manager", "super_admin"],
    ps_codes=["PS-06.08"],
))


# ═══════════════════════════════════════════════════════════════════════════════
# 62. stylist_career_path (PS-06.09)
# ═══════════════════════════════════════════════════════════════════════════════

async def stylist_career_path_handler(
    staff_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["stylist", "salon_manager", "franchise_owner", "regional_manager"])),
):
    """Career path view: current level, competencies, projected promotion, earnings."""
    now = datetime.now(timezone.utc)

    # Get staff profile
    staff_result = await db.execute(
        select(StaffProfile).where(StaffProfile.id == staff_id)
    )
    staff = staff_result.scalar_one_or_none()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    current_level = enum_val(staff.skill_level) if staff.skill_level else "L1"

    # Determine next level
    level_progression = {"L1": "L2", "L2": "L3", "L3": "Master"}
    next_level = level_progression.get(current_level, "N/A")

    # Get all skill assessments for this staff
    assessments_result = await db.execute(
        select(SkillAssessment).where(
            SkillAssessment.staff_id == staff_id,
        ).order_by(SkillAssessment.created_at.desc())
    )
    assessments = assessments_result.scalars().all()

    # Deduplicate by skill area (keep most recent)
    seen_skills = set()
    unique_assessments = []
    for a in assessments:
        key = a.skill_area or a.service_category or "general"
        if key not in seen_skills:
            seen_skills.add(key)
            unique_assessments.append(a)

    # Competencies met: score >= 7.0
    competencies_met = [
        {
            "skill": a.skill_area or a.service_category,
            "score": float(a.score) if a.score else 0,
            "status": "met",
        }
        for a in unique_assessments if a.score and float(a.score) >= 7.0
    ]

    # Competencies needed: score < 7.0 or gaps identified
    competencies_needed = []
    for a in unique_assessments:
        if a.score and float(a.score) < 7.0:
            # Check if training is available
            training_available_result = await db.execute(
                select(TrainingRecord.training_name).where(
                    TrainingRecord.service_category == a.service_category,
                ).order_by(TrainingRecord.created_at.desc()).limit(1)
            )
            training_name = training_available_result.scalar_one_or_none()

            competencies_needed.append({
                "skill": a.skill_area or a.service_category,
                "current_score": float(a.score),
                "required_score": 7.0,
                "gap": round(7.0 - float(a.score), 2),
                "training_available": training_name,
            })

    # Add gap items from L2/L3 gap analysis
    for a in unique_assessments:
        if current_level == "L1" and a.l2_gap_items:
            for gap in a.l2_gap_items:
                if not any(c["skill"] == gap for c in competencies_needed):
                    competencies_needed.append({
                        "skill": gap,
                        "current_score": None,
                        "required_score": 7.0,
                        "gap": None,
                        "training_available": None,
                    })
        elif current_level == "L2" and a.l3_gap_items:
            for gap in a.l3_gap_items:
                if not any(c["skill"] == gap for c in competencies_needed):
                    competencies_needed.append({
                        "skill": gap,
                        "current_score": None,
                        "required_score": 7.0,
                        "gap": None,
                        "training_available": None,
                    })

    # Projected promotion date: estimate based on gap count and training duration
    gaps_remaining = len(competencies_needed)
    weeks_per_skill = 4
    projected_weeks = gaps_remaining * weeks_per_skill
    projected_promotion_date = str((now + timedelta(weeks=projected_weeks)).date()) if gaps_remaining > 0 else "Eligible now"

    # Earnings brackets (industry estimates)
    earnings_brackets = {
        "L1": {"min": 15000, "max": 25000, "label": "L1 (15,000 - 25,000)"},
        "L2": {"min": 25000, "max": 40000, "label": "L2 (25,000 - 40,000)"},
        "L3": {"min": 40000, "max": 65000, "label": "L3 (40,000 - 65,000)"},
        "Master": {"min": 65000, "max": 100000, "label": "Master (65,000 - 100,000)"},
    }
    current_bracket = earnings_brackets.get(current_level, earnings_brackets["L1"])
    next_bracket = earnings_brackets.get(next_level, current_bracket)
    earnings_increase_pct = round(
        (next_bracket["min"] - current_bracket["min"]) / max(current_bracket["min"], 1) * 100, 1
    )

    # Mentor — find a higher-level stylist at same location
    mentor_result = await db.execute(
        select(StaffProfile.id, User.first_name, User.last_name)
        .join(User, User.id == StaffProfile.user_id)
        .where(
            StaffProfile.location_id == staff.location_id,
            StaffProfile.id != staff_id,
            StaffProfile.skill_level != None,
        )
        .order_by(StaffProfile.skill_level.desc())
        .limit(1)
    )
    mentor_row = mentor_result.first()
    mentor = {
        "staff_id": mentor_row.id,
        "name": f"{mentor_row.first_name} {mentor_row.last_name}",
    } if mentor_row else None

    return APIResponse(
        success=True,
        data={
            "staff_id": staff_id,
            "current_level": current_level,
            "next_level": next_level,
            "competencies_met": competencies_met,
            "competencies_needed": competencies_needed,
            "projected_promotion_date": projected_promotion_date,
            "current_earnings_bracket": current_bracket["label"],
            "next_level_earnings_bracket": next_bracket["label"],
            "earnings_increase_pct": earnings_increase_pct,
            "mentor_assigned": mentor,
            "years_experience": float(staff.years_experience) if staff.years_experience else None,
        },
    )


agent_career_path = register_agent(AgentAction(
    name="stylist_career_path",
    description="Career path view with current competencies, gaps, projected promotion, and earnings trajectory",
    track="intelligence",
    feature="career_path",
    method="get",
    path="/agents/track6/career/path",
    handler=stylist_career_path_handler,
    roles=["stylist", "salon_manager", "franchise_owner", "regional_manager"],
    ps_codes=["PS-06.09"],
))


# ═══════════════════════════════════════════════════════════════════════════════
# 63. service_portfolio_optimizer (PS-06.10)
# ═══════════════════════════════════════════════════════════════════════════════

async def service_portfolio_optimizer_handler(
    location_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "franchise_owner", "regional_manager", "super_admin"])),
):
    """Analyze service portfolio at a location: flag services to expand, de-emphasize, or introduce."""
    now = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)
    sixty_days_ago = now - timedelta(days=60)

    # Verify location
    loc_result = await db.execute(
        select(Location).where(Location.id == location_id)
    )
    location = loc_result.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    # Get all active services booked at this location
    svc_result = await db.execute(
        select(
            Service.id,
            Service.name,
            Service.category,
            Service.base_price,
            Service.duration_minutes,
            func.count(Booking.id).label("bookings_30d"),
            func.sum(Booking.final_price).label("revenue_30d"),
            func.avg(QualityAssessment.overall_score).label("quality_avg"),
        )
        .outerjoin(Booking, and_(
            Booking.service_id == Service.id,
            Booking.location_id == location_id,
            Booking.status == BookingStatus.COMPLETED,
            Booking.actual_end_at >= thirty_days_ago,
        ))
        .outerjoin(QualityAssessment, and_(
            QualityAssessment.service_id == Service.id,
            QualityAssessment.location_id == location_id,
            QualityAssessment.created_at >= thirty_days_ago,
        ))
        .where(Service.is_active == True)
        .group_by(Service.id, Service.name, Service.category, Service.base_price, Service.duration_minutes)
        .having(func.count(Booking.id) > 0)
        .order_by(func.sum(Booking.final_price).desc())
    )
    current_services = svc_result.all()

    # Previous 30d bookings for demand trend
    prev_bookings_result = await db.execute(
        select(
            Booking.service_id,
            func.count(Booking.id).label("prev_count"),
        )
        .where(
            Booking.location_id == location_id,
            Booking.status == BookingStatus.COMPLETED,
            Booking.actual_end_at >= sixty_days_ago,
            Booking.actual_end_at < thirty_days_ago,
        )
        .group_by(Booking.service_id)
    )
    prev_counts = {row.service_id: row.prev_count for row in prev_bookings_result.all()}

    # Total location revenue for utilization calculation
    total_revenue = sum(float(s.revenue_30d or 0) for s in current_services)

    portfolio = []
    for svc in current_services:
        bookings_30d = svc.bookings_30d or 0
        revenue_30d = round(float(svc.revenue_30d or 0), 2)
        quality_avg = round(float(svc.quality_avg or 0), 2)
        prev_count = prev_counts.get(svc.id, 0)

        # Utilization: this service's revenue share
        utilization_pct = round(revenue_30d / max(total_revenue, 1) * 100, 1)

        # Margin estimate: higher-price services = higher margin
        base_price = float(svc.base_price or 0)
        margin_pct = 65.0 if base_price >= 1000 else (55.0 if base_price >= 500 else 45.0)

        # Demand trend
        if prev_count > 0:
            demand_change = (bookings_30d - prev_count) / prev_count * 100
            if demand_change > 15:
                demand_trend = "growing"
            elif demand_change < -15:
                demand_trend = "declining"
            else:
                demand_trend = "stable"
        else:
            demand_trend = "new"

        # Flag logic
        if demand_trend == "growing" and margin_pct >= 55 and bookings_30d >= 5:
            flag = "EXPAND"
        elif demand_trend == "declining" and margin_pct < 55 and bookings_30d < 3:
            flag = "DE-EMPHASIZE"
        else:
            flag = "MAINTAIN"

        portfolio.append({
            "service_id": svc.id,
            "service_name": svc.name,
            "category": svc.category,
            "bookings_30d": bookings_30d,
            "revenue_30d": revenue_30d,
            "utilization_pct": utilization_pct,
            "margin_pct": margin_pct,
            "quality_avg": quality_avg,
            "demand_trend": demand_trend,
            "flag": flag,
        })

    # Services to INTRODUCE: trending regionally but not offered at this location
    offered_categories = {s["category"] for s in portfolio if s["category"]}
    trending_result = await db.execute(
        select(TrendSignal.trend_name, TrendSignal.service_category)
        .where(
            TrendSignal.is_active == True,
            TrendSignal.trajectory.in_([TrendTrajectory.EMERGING, TrendTrajectory.GROWING]),
            ~TrendSignal.service_category.in_(offered_categories) if offered_categories else literal(True),
        )
        .order_by(TrendSignal.overall_signal_strength.desc())
        .limit(3)
    )
    services_to_introduce = [
        {
            "trend_name": row.trend_name,
            "service_category": row.service_category,
            "reason": "Trending locally but not yet offered at this location",
        }
        for row in trending_result.all()
    ]

    # Summary counts
    expand_count = sum(1 for s in portfolio if s["flag"] == "EXPAND")
    de_emphasize_count = sum(1 for s in portfolio if s["flag"] == "DE-EMPHASIZE")

    return APIResponse(
        success=True,
        data={
            "location_id": location_id,
            "location_name": location.name,
            "portfolio": portfolio,
            "services_to_introduce": services_to_introduce,
            "summary": {
                "total_services_analyzed": len(portfolio),
                "expand": expand_count,
                "de_emphasize": de_emphasize_count,
                "maintain": len(portfolio) - expand_count - de_emphasize_count,
                "introduce": len(services_to_introduce),
                "total_revenue_30d": round(total_revenue, 2),
            },
        },
    )


agent_portfolio_optimizer = register_agent(AgentAction(
    name="service_portfolio_optimizer",
    description="Analyze service portfolio to flag services for expansion, de-emphasis, or introduction",
    track="intelligence",
    feature="portfolio",
    method="get",
    path="/agents/track6/portfolio/optimize",
    handler=service_portfolio_optimizer_handler,
    roles=["salon_manager", "franchise_owner", "regional_manager", "super_admin"],
    ps_codes=["PS-06.10"],
))
