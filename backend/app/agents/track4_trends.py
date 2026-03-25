"""Track 4: Trend Intelligence — 10 agents for trend detection, predictive
inventory, regional mapping, celebrity alerts, seasonal forecasting, social
ingestion, training gaps, competitor intel, product launch timing, and
campaign recommendations.
"""
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Query
from sqlalchemy import select, func, desc, and_, extract, case, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, generate_uuid, enum_val
from app.dependencies import get_current_user, require_role
from app.models.user import User
from app.models.customer import CustomerProfile
from app.models.booking import Booking, BookingStatus
from app.models.service import Service
from app.models.trend import TrendSignal, TrendTrajectory, TrendLongevity
from app.models.location import Location
from app.models.staff import StaffProfile
from app.models.training import TrainingRecord
from app.models.inventory import InventoryItem
from app.models.campaign import Campaign, CompetitiveIntel, CelebrityTrendSource
from app.schemas.common import APIResponse
from app.agents import AgentAction, register_agent


# ─────────────────────────────────────────────────────────────────────────────
# 34. trend_early_detection  (PS-04.01)
# ─────────────────────────────────────────────────────────────────────────────

async def trend_early_detection_handler(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "regional_manager", "franchise_owner", "super_admin"])),
):
    """Return all active trends sorted by signal strength with readiness status per location."""

    # ── Active trends sorted by signal strength ──
    trend_result = await db.execute(
        select(TrendSignal)
        .where(TrendSignal.is_active == True)
        .order_by(desc(TrendSignal.overall_signal_strength))
    )
    trends = trend_result.scalars().all()

    # ── Get all active locations ──
    loc_result = await db.execute(
        select(Location).where(Location.is_active == True)
    )
    locations = loc_result.scalars().all()

    # ── For each trend, compute readiness per location ──
    output_trends = []
    action_needed = []

    for trend in trends:
        signal_strength = float(trend.overall_signal_strength) if trend.overall_signal_strength else 0
        trend_category = trend.service_category
        applicable_cities = trend.applicable_cities or []

        location_readiness = []
        for loc in locations:
            # Filter by applicable cities if specified
            if applicable_cities and loc.city not in applicable_cities:
                continue

            # Check staff training: do any staff at this location have training in this category?
            training_result = await db.execute(
                select(func.count(TrainingRecord.id))
                .join(StaffProfile, StaffProfile.id == TrainingRecord.staff_id)
                .where(
                    StaffProfile.location_id == loc.id,
                    TrainingRecord.passed == True,
                    func.lower(TrainingRecord.service_category) == func.lower(trend_category) if trend_category else True,
                )
            )
            trained_count = training_result.scalar() or 0
            staff_trained = trained_count > 0

            # Check inventory: are products stocked for this category?
            inv_result = await db.execute(
                select(func.count(InventoryItem.id))
                .where(
                    InventoryItem.location_id == loc.id,
                    InventoryItem.is_active == True,
                    func.lower(InventoryItem.category) == func.lower(trend_category) if trend_category else True,
                    InventoryItem.current_stock > 0,
                )
            )
            products_stocked = (inv_result.scalar() or 0) > 0

            # Check SOP: does a service exist for this category?
            svc_result = await db.execute(
                select(func.count(Service.id))
                .where(
                    Service.is_active == True,
                    func.lower(Service.category) == func.lower(trend_category) if trend_category else True,
                    Service.sop_id.isnot(None),
                )
            )
            sop_exists = (svc_result.scalar() or 0) > 0

            ready = staff_trained and products_stocked and sop_exists

            location_readiness.append({
                "location_id": loc.id,
                "location_name": loc.name,
                "city": loc.city,
                "staff_trained": staff_trained,
                "products_stocked": products_stocked,
                "sop_exists": sop_exists,
                "ready": ready,
            })

        # Identify action-needed trends: high signal, low readiness
        not_ready_count = sum(1 for lr in location_readiness if not lr["ready"])
        total_locations_checked = len(location_readiness)

        trend_entry = {
            "trend_id": trend.id,
            "trend_name": trend.trend_name,
            "description": trend.description,
            "service_category": trend.service_category,
            "signal_strength": signal_strength,
            "trajectory": enum_val(trend.trajectory) if trend.trajectory else None,
            "longevity": enum_val(trend.longevity_label) if trend.longevity_label else None,
            "predicted_peak_date": str(trend.predicted_peak_date) if trend.predicted_peak_date else None,
            "social_media_score": float(trend.social_media_score) if trend.social_media_score else None,
            "influencer_score": float(trend.influencer_score) if trend.influencer_score else None,
            "celebrity_trigger": trend.celebrity_trigger,
            "locations_checked": total_locations_checked,
            "locations_ready": total_locations_checked - not_ready_count,
            "locations_not_ready": not_ready_count,
            "readiness_by_location": location_readiness,
        }
        output_trends.append(trend_entry)

        if signal_strength >= 5.0 and not_ready_count > 0:
            action_needed.append({
                "trend_name": trend.trend_name,
                "signal_strength": signal_strength,
                "not_ready_locations": not_ready_count,
                "gaps": [lr for lr in location_readiness if not lr["ready"]],
            })

    return APIResponse(
        success=True,
        data={
            "total_active_trends": len(trends),
            "action_needed_count": len(action_needed),
            "trends": output_trends,
            "action_needed": action_needed,
        },
    )


trend_early_detection_agent = register_agent(AgentAction(
    name="trend_early_detection",
    description="Active trends sorted by signal strength with per-location readiness status and action alerts",
    track="trends",
    feature="detection",
    method="get",
    path="/agents/track4/trends/early-detection",
    handler=trend_early_detection_handler,
    roles=["salon_manager", "regional_manager", "franchise_owner", "super_admin"],
    ps_codes=["PS-04.01"],
))


# ─────────────────────────────────────────────────────────────────────────────
# 35. predictive_inventory  (PS-04.02)
# ─────────────────────────────────────────────────────────────────────────────

async def predictive_inventory_handler(
    location_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "regional_manager", "franchise_owner", "super_admin"])),
):
    """Analyze trends, seasonal patterns, and booking velocity to produce inventory recommendations."""

    loc_result = await db.execute(select(Location).where(Location.id == location_id))
    location = loc_result.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    # ── Current month and next month ──
    now = datetime.now(timezone.utc)
    current_month = now.month
    next_month = current_month + 1 if current_month < 12 else 1
    next_month_year = now.year if current_month < 12 else now.year + 1

    # ── Booking velocity per service category this month ──
    current_demand_result = await db.execute(
        select(Service.category, func.count(Booking.id).label("cnt"))
        .join(Booking, Booking.service_id == Service.id)
        .where(
            Booking.location_id == location_id,
            Booking.status.in_([BookingStatus.COMPLETED, BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS]),
            extract("month", Booking.scheduled_at) == current_month,
            extract("year", Booking.scheduled_at) == now.year,
        )
        .group_by(Service.category)
    )
    current_demand_map: dict[str, int] = {}
    for row in current_demand_result.all():
        if row[0]:
            current_demand_map[row[0]] = row[1]

    # ── Historical bookings for next month (last year's same month) ──
    hist_result = await db.execute(
        select(Service.category, func.count(Booking.id).label("cnt"))
        .join(Booking, Booking.service_id == Service.id)
        .where(
            Booking.location_id == location_id,
            Booking.status == BookingStatus.COMPLETED,
            extract("month", Booking.scheduled_at) == next_month,
            extract("year", Booking.scheduled_at) == now.year - 1,
        )
        .group_by(Service.category)
    )
    historical_map: dict[str, int] = {}
    for row in hist_result.all():
        if row[0]:
            historical_map[row[0]] = row[1]

    # ── Trending categories ──
    trend_result = await db.execute(
        select(TrendSignal.service_category, TrendSignal.overall_signal_strength)
        .where(
            TrendSignal.is_active == True,
            TrendSignal.overall_signal_strength > 3.0,
        )
        .order_by(desc(TrendSignal.overall_signal_strength))
    )
    trending_cats: dict[str, float] = {}
    for row in trend_result.all():
        if row[0]:
            trending_cats[row[0]] = float(row[1])

    # ── Inventory items at this location ──
    inv_result = await db.execute(
        select(InventoryItem)
        .where(InventoryItem.location_id == location_id, InventoryItem.is_active == True)
    )
    inventory_items = inv_result.scalars().all()

    # ── Build recommendations per product category ──
    all_categories = set(current_demand_map.keys()) | set(historical_map.keys()) | set(trending_cats.keys())

    recommendations = []
    for cat in sorted(all_categories):
        current = current_demand_map.get(cat, 0)
        historical = historical_map.get(cat, 0)
        trend_boost = trending_cats.get(cat, 0)

        # Predict next month demand: weighted average of historical + current velocity + trend
        if historical > 0:
            predicted = int(historical * 0.5 + current * 0.3 + (current * trend_boost / 10) * 0.2)
        else:
            predicted = int(current * 1.1 + (current * trend_boost / 10) * 0.2)

        predicted = max(predicted, 1)

        # Determine action
        if predicted > current * 1.3:
            action = "increase"
            quantity_adj = predicted - current
        elif predicted < current * 0.7:
            action = "decrease"
            quantity_adj = current - predicted
        else:
            action = "maintain"
            quantity_adj = 0

        recommendations.append({
            "product_category": cat,
            "current_month_bookings": current,
            "historical_same_month_bookings": historical,
            "trend_signal_strength": trend_boost if trend_boost else None,
            "predicted_demand_next_month": predicted,
            "action": action,
            "quantity_adjustment": quantity_adj,
        })

    # Sort by predicted demand descending
    recommendations.sort(key=lambda x: x["predicted_demand_next_month"], reverse=True)

    return APIResponse(
        success=True,
        data={
            "location_id": location_id,
            "location_name": location.name,
            "city": location.city,
            "analysis_month": f"{now.year}-{current_month:02d}",
            "forecast_month": f"{next_month_year}-{next_month:02d}",
            "categories_analyzed": len(recommendations),
            "inventory_items_at_location": len(inventory_items),
            "recommendations": recommendations,
        },
    )


predictive_inventory_agent = register_agent(AgentAction(
    name="predictive_inventory",
    description="Predict next-month inventory needs based on trends, seasonality, and booking velocity",
    track="trends",
    feature="inventory",
    method="post",
    path="/agents/track4/inventory/predictive",
    handler=predictive_inventory_handler,
    roles=["salon_manager", "regional_manager", "franchise_owner", "super_admin"],
    ps_codes=["PS-04.02"],
))


# ─────────────────────────────────────────────────────────────────────────────
# 36. regional_trend_map  (PS-04.03)
# ─────────────────────────────────────────────────────────────────────────────

async def regional_trend_map_handler(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "regional_manager", "franchise_owner", "super_admin"])),
):
    """Return trends broken down by city/region with signal strength and trajectory."""

    trend_result = await db.execute(
        select(TrendSignal)
        .where(TrendSignal.is_active == True)
        .order_by(desc(TrendSignal.overall_signal_strength))
    )
    trends = trend_result.scalars().all()

    # ── Get all distinct cities from locations ──
    city_result = await db.execute(
        select(distinct(Location.city), Location.region)
        .where(Location.is_active == True)
    )
    city_rows = city_result.all()
    all_cities = {row[0]: row[1] for row in city_rows}

    # ── Build per-trend city breakdown ──
    trend_map = []
    for trend in trends:
        signal = float(trend.overall_signal_strength) if trend.overall_signal_strength else 0
        applicable_cities = trend.applicable_cities or list(all_cities.keys())

        cities_data = []
        for city in applicable_cities:
            if city not in all_cities:
                continue

            # Count bookings in this city for this trend's category in last 30 days
            bk_count_result = await db.execute(
                select(func.count(Booking.id))
                .join(Service, Service.id == Booking.service_id)
                .join(Location, Location.id == Booking.location_id)
                .where(
                    Location.city == city,
                    Booking.status.in_([BookingStatus.COMPLETED, BookingStatus.CONFIRMED]),
                    Booking.scheduled_at >= datetime.now(timezone.utc) - timedelta(days=30),
                    func.lower(Service.category) == func.lower(trend.service_category) if trend.service_category else True,
                )
            )
            city_bookings = bk_count_result.scalar() or 0

            # Compute city-level signal based on bookings + overall
            city_signal = min(10.0, signal * (1 + city_bookings / max(city_bookings + 10, 1)))

            # Determine stage
            trajectory = trend.trajectory
            if trajectory == TrendTrajectory.EMERGING:
                stage = "emerging"
            elif trajectory == TrendTrajectory.GROWING:
                stage = "emerging" if city_bookings < 5 else "mainstream"
            elif trajectory == TrendTrajectory.PEAK:
                stage = "mainstream"
            elif trajectory == TrendTrajectory.DECLINING:
                stage = "declining"
            else:
                stage = "emerging"

            cities_data.append({
                "city": city,
                "region": all_cities.get(city),
                "signal_strength": round(city_signal, 2),
                "local_bookings_30d": city_bookings,
                "trajectory": enum_val(trajectory) if trajectory else None,
                "stage": stage,
            })

        # Sort cities by signal strength
        cities_data.sort(key=lambda x: x["signal_strength"], reverse=True)

        trend_map.append({
            "trend_id": trend.id,
            "trend_name": trend.trend_name,
            "service_category": trend.service_category,
            "overall_signal": signal,
            "longevity": enum_val(trend.longevity_label) if trend.longevity_label else None,
            "cities": cities_data,
        })

    # Regional highlights: biggest differences
    regional_highlights = []
    for tm in trend_map:
        if len(tm["cities"]) >= 2:
            strongest = tm["cities"][0]
            weakest = tm["cities"][-1]
            diff = strongest["signal_strength"] - weakest["signal_strength"]
            if diff > 2.0:
                regional_highlights.append({
                    "trend_name": tm["trend_name"],
                    "strongest_city": strongest["city"],
                    "strongest_signal": strongest["signal_strength"],
                    "weakest_city": weakest["city"],
                    "weakest_signal": weakest["signal_strength"],
                    "spread": round(diff, 2),
                })

    return APIResponse(
        success=True,
        data={
            "total_trends": len(trend_map),
            "cities_covered": len(all_cities),
            "regional_highlights": regional_highlights,
            "trend_map": trend_map,
        },
    )


regional_trend_map_agent = register_agent(AgentAction(
    name="regional_trend_map",
    description="Trends broken down by city/region with per-city signal strength, stage, and trajectory",
    track="trends",
    feature="regional",
    method="get",
    path="/agents/track4/trends/regional-map",
    handler=regional_trend_map_handler,
    roles=["salon_manager", "regional_manager", "franchise_owner", "super_admin"],
    ps_codes=["PS-04.03"],
))


# ─────────────────────────────────────────────────────────────────────────────
# 37. celebrity_trend_alert  (PS-04.04)
# ─────────────────────────────────────────────────────────────────────────────

async def celebrity_trend_alert_handler(
    celebrity_name: str = Query(...),
    look_type: str = Query(..., description="e.g., bob cut, balayage, glass skin"),
    source_media: str = Query(..., description="e.g., instagram, bollywood, event"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "regional_manager", "super_admin"])),
):
    """Create a trend signal from a celebrity look and predict demand spike."""

    # ── Determine service category from look_type ──
    look_lower = look_type.lower()
    if any(w in look_lower for w in ["cut", "bob", "pixie", "layers", "bangs", "shag"]):
        category = "haircut"
    elif any(w in look_lower for w in ["color", "balayage", "highlights", "ombre", "blonde", "red"]):
        category = "hair color"
    elif any(w in look_lower for w in ["skin", "glass", "glow", "facial"]):
        category = "facial"
    elif any(w in look_lower for w in ["makeup", "smokey", "glam", "dewy"]):
        category = "makeup"
    elif any(w in look_lower for w in ["nail", "manicure"]):
        category = "manicure"
    else:
        category = "hair styling"

    # ── Check for existing trend with similar name ──
    slug = f"celeb-{celebrity_name.lower().replace(' ', '-')}-{look_lower.replace(' ', '-')}"
    existing_result = await db.execute(
        select(TrendSignal).where(TrendSignal.slug == slug)
    )
    existing = existing_result.scalar_one_or_none()

    if existing:
        # Update signal strength
        current = float(existing.overall_signal_strength) if existing.overall_signal_strength else 5.0
        existing.overall_signal_strength = min(10.0, current + 1.0)
        existing.celebrity_trigger = celebrity_name
        trend_id = existing.id
        action = "updated_existing"
    else:
        # Create new trend signal
        trend = TrendSignal(
            trend_name=f"{celebrity_name} — {look_type}",
            slug=slug,
            description=f"Celebrity trend: {celebrity_name}'s {look_type} look spotted on {source_media}",
            service_category=category,
            overall_signal_strength=6.5,
            social_media_score=7.0,
            influencer_score=8.0,
            celebrity_trigger=celebrity_name,
            trajectory=TrendTrajectory.EMERGING,
            longevity_label=TrendLongevity.TREND,
            predicted_peak_date=date.today() + timedelta(weeks=4),
            confidence_level=0.70,
            detected_at=datetime.now(timezone.utc),
            is_active=True,
        )
        db.add(trend)
        await db.flush()
        trend_id = trend.id
        action = "created_new"

    # ── Create celebrity trend source record ──
    celeb_source = CelebrityTrendSource(
        celebrity_name=celebrity_name,
        media_source=source_media,
        look_description=look_type,
        detected_services=[category],
        virality_score=7.0,
        linked_trend_id=trend_id,
        detected_at=datetime.now(timezone.utc),
    )
    db.add(celeb_source)

    # ── Get locations that need preparation ──
    loc_result = await db.execute(
        select(Location.id, Location.name, Location.city)
        .where(Location.is_active == True)
    )
    branches = [{"location_id": r[0], "name": r[1], "city": r[2]} for r in loc_result.all()]

    # ── Determine training needs ──
    training_needed = []
    staff_result = await db.execute(
        select(StaffProfile.id, StaffProfile.location_id, StaffProfile.specializations)
        .where(StaffProfile.is_available == True)
    )
    for sp in staff_result.all():
        specs = sp[2] or []
        if not any(category.lower() in s.lower() for s in specs):
            training_needed.append(sp[0])

    predicted_peak = date.today() + timedelta(weeks=4)

    return APIResponse(
        success=True,
        data={
            "trend_created": action,
            "trend_id": trend_id,
            "celebrity": celebrity_name,
            "look_type": look_type,
            "service_category": category,
            "source_media": source_media,
            "predicted_peak_date": str(predicted_peak),
            "predicted_demand_spike_weeks": 4,
            "branches_to_prepare": len(branches),
            "branches": branches,
            "training_needed_for": len(training_needed),
            "staff_needing_training_ids": training_needed[:20],
        },
    )


celebrity_trend_alert_agent = register_agent(AgentAction(
    name="celebrity_trend_alert",
    description="Create a trend signal from a celebrity look and predict demand spike timeline",
    track="trends",
    feature="celebrity",
    method="post",
    path="/agents/track4/trends/celebrity-alert",
    handler=celebrity_trend_alert_handler,
    roles=["salon_manager", "regional_manager", "super_admin"],
    ps_codes=["PS-04.04"],
))


# ─────────────────────────────────────────────────────────────────────────────
# 38. seasonal_demand_forecast  (PS-04.05)
# ─────────────────────────────────────────────────────────────────────────────

async def seasonal_demand_forecast_handler(
    location_id: str = Query(...),
    months_ahead: int = Query(3, ge=1, le=6),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "regional_manager", "franchise_owner", "super_admin"])),
):
    """Forecast demand per service category for upcoming months using historical booking data."""

    loc_result = await db.execute(select(Location).where(Location.id == location_id))
    location = loc_result.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    now = datetime.now(timezone.utc)
    forecasts = []

    for offset in range(1, months_ahead + 1):
        target_month = (now.month + offset - 1) % 12 + 1
        target_year = now.year + (now.month + offset - 1) // 12

        # ── Historical bookings for this month (1 and 2 years ago) ──
        hist_result = await db.execute(
            select(Service.category, func.count(Booking.id).label("cnt"))
            .join(Booking, Booking.service_id == Service.id)
            .where(
                Booking.location_id == location_id,
                Booking.status == BookingStatus.COMPLETED,
                extract("month", Booking.scheduled_at) == target_month,
                extract("year", Booking.scheduled_at).in_([now.year - 1, now.year - 2]),
            )
            .group_by(Service.category)
        )
        historical_data: dict[str, list[int]] = {}
        for row in hist_result.all():
            cat = row[0] or "General"
            historical_data.setdefault(cat, []).append(row[1])

        # ── Current year bookings for same month (if past or current) ──
        current_result = await db.execute(
            select(Service.category, func.count(Booking.id).label("cnt"))
            .join(Booking, Booking.service_id == Service.id)
            .where(
                Booking.location_id == location_id,
                Booking.status.in_([BookingStatus.COMPLETED, BookingStatus.CONFIRMED]),
                extract("month", Booking.scheduled_at) == now.month,
                extract("year", Booking.scheduled_at) == now.year,
            )
            .group_by(Service.category)
        )
        current_map: dict[str, int] = {}
        for row in current_result.all():
            if row[0]:
                current_map[row[0]] = row[1]

        # ── Compute predictions ──
        all_cats = set(historical_data.keys()) | set(current_map.keys())

        for cat in sorted(all_cats):
            hist_values = historical_data.get(cat, [])
            current = current_map.get(cat, 0)
            avg_hist = sum(hist_values) / len(hist_values) if hist_values else current

            # Growth factor from current year
            growth_factor = (current / avg_hist) if avg_hist > 0 else 1.0
            growth_factor = min(growth_factor, 2.0)  # cap at 2x

            predicted = int(avg_hist * growth_factor)
            predicted = max(predicted, 1)

            # Confidence: higher with more historical data
            confidence = 0.5 + min(len(hist_values) * 0.15, 0.4)

            # Staffing recommendation
            avg_services_per_stylist_per_day = 6
            working_days = 26
            stylists_needed = max(1, predicted // (avg_services_per_stylist_per_day * working_days) + 1)

            forecasts.append({
                "month": f"{target_year}-{target_month:02d}",
                "service_category": cat,
                "historical_avg": round(avg_hist, 1),
                "growth_factor": round(growth_factor, 2),
                "predicted_bookings": predicted,
                "confidence": round(confidence, 2),
                "staffing_recommendation": f"{stylists_needed} stylists needed for this category",
                "inventory_recommendation": "Increase stock by 20%" if growth_factor > 1.2 else "Maintain current stock levels",
            })

    # Sort by month then predicted bookings
    forecasts.sort(key=lambda x: (x["month"], -x["predicted_bookings"]))

    return APIResponse(
        success=True,
        data={
            "location_id": location_id,
            "location_name": location.name,
            "city": location.city,
            "forecast_period": f"{months_ahead} months ahead",
            "total_forecasts": len(forecasts),
            "forecasts": forecasts,
        },
    )


seasonal_demand_forecast_agent = register_agent(AgentAction(
    name="seasonal_demand_forecast",
    description="Forecast demand per service category for upcoming months using historical and current booking data",
    track="trends",
    feature="forecast",
    method="get",
    path="/agents/track4/forecast/seasonal-demand",
    handler=seasonal_demand_forecast_handler,
    roles=["salon_manager", "regional_manager", "franchise_owner", "super_admin"],
    ps_codes=["PS-04.05"],
))


# ─────────────────────────────────────────────────────────────────────────────
# 39. social_trend_ingest  (PS-04.06)
# ─────────────────────────────────────────────────────────────────────────────

async def social_trend_ingest_handler(
    trend_data: dict = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "regional_manager", "super_admin"])),
):
    """Evaluate a social media trend signal and create/update TrendSignal if strong enough."""

    if not trend_data:
        raise HTTPException(status_code=400, detail="trend_data is required")

    platform = trend_data.get("platform", "unknown")
    content_type = trend_data.get("content_type", "post")
    engagement = trend_data.get("engagement_metrics", {})
    beauty_category = trend_data.get("beauty_category", "general")
    description = trend_data.get("description", "")

    # ── Evaluate signal strength from engagement ──
    likes = engagement.get("likes", 0)
    shares = engagement.get("shares", 0)
    comments = engagement.get("comments", 0)
    views = engagement.get("views", 0)
    saves = engagement.get("saves", 0)

    # Weighted signal calculation
    engagement_score = (
        likes * 0.1 +
        shares * 0.5 +
        comments * 0.3 +
        saves * 0.4 +
        views * 0.01
    )
    # Normalize to 0-10 scale
    signal_strength = min(10.0, max(0.0, engagement_score / 1000))

    # Platform multipliers
    platform_multipliers = {
        "instagram": 1.2,
        "tiktok": 1.3,
        "youtube": 1.1,
        "pinterest": 1.0,
        "twitter": 0.8,
        "facebook": 0.7,
    }
    multiplier = platform_multipliers.get(platform.lower(), 1.0)
    signal_strength *= multiplier
    signal_strength = min(10.0, signal_strength)

    # ── Decide action ──
    threshold = 3.0
    action_taken = "ignored"
    trend_id = None

    if signal_strength >= threshold:
        # Check if similar trend exists
        slug = f"social-{beauty_category.lower().replace(' ', '-')}-{platform.lower()}"
        existing_result = await db.execute(
            select(TrendSignal).where(
                TrendSignal.service_category == beauty_category,
                TrendSignal.is_active == True,
            )
            .order_by(desc(TrendSignal.overall_signal_strength))
            .limit(1)
        )
        existing = existing_result.scalar_one_or_none()

        if existing:
            # Update existing trend
            old_strength = float(existing.overall_signal_strength) if existing.overall_signal_strength else 0
            existing.overall_signal_strength = min(10.0, (old_strength + signal_strength) / 2 + 0.5)
            existing.social_media_score = min(10.0, signal_strength)
            trend_id = existing.id
            action_taken = "updated_existing"
        else:
            # Create new trend
            trajectory = TrendTrajectory.EMERGING if signal_strength < 6 else TrendTrajectory.GROWING
            trend = TrendSignal(
                trend_name=f"Social trend: {beauty_category} ({platform})",
                slug=f"social-{generate_uuid()[:8]}",
                description=description or f"Trending {beauty_category} content on {platform}",
                service_category=beauty_category,
                overall_signal_strength=signal_strength,
                social_media_score=signal_strength,
                trajectory=trajectory,
                longevity_label=TrendLongevity.FAD if signal_strength < 5 else TrendLongevity.TREND,
                predicted_peak_date=date.today() + timedelta(weeks=3),
                confidence_level=min(0.95, signal_strength / 10),
                detected_at=datetime.now(timezone.utc),
                source_urls=[trend_data.get("url")] if trend_data.get("url") else None,
                is_active=True,
            )
            db.add(trend)
            await db.flush()
            trend_id = trend.id
            action_taken = "created_new"

    return APIResponse(
        success=True,
        data={
            "signal_evaluated": True,
            "platform": platform,
            "beauty_category": beauty_category,
            "engagement_metrics": engagement,
            "computed_signal_strength": round(signal_strength, 2),
            "threshold": threshold,
            "above_threshold": signal_strength >= threshold,
            "action_taken": action_taken,
            "trend_id": trend_id,
        },
    )


social_trend_ingest_agent = register_agent(AgentAction(
    name="social_trend_ingest",
    description="Evaluate social media trend signals and create/update TrendSignal records",
    track="trends",
    feature="social",
    method="post",
    path="/agents/track4/trends/social-ingest",
    handler=social_trend_ingest_handler,
    roles=["salon_manager", "regional_manager", "super_admin"],
    ps_codes=["PS-04.06"],
))


# ─────────────────────────────────────────────────────────────────────────────
# 40. trend_linked_training  (PS-04.07)
# ─────────────────────────────────────────────────────────────────────────────

async def trend_linked_training_handler(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "regional_manager", "franchise_owner", "super_admin"])),
):
    """Return trends blocked by skill gaps with training needs per branch."""

    # ── Active trends ──
    trend_result = await db.execute(
        select(TrendSignal)
        .where(TrendSignal.is_active == True, TrendSignal.overall_signal_strength > 3.0)
        .order_by(desc(TrendSignal.overall_signal_strength))
    )
    trends = trend_result.scalars().all()

    # ── All active staff ──
    staff_result = await db.execute(
        select(StaffProfile)
        .where(StaffProfile.is_available == True)
    )
    all_staff = staff_result.scalars().all()

    # ── All training records ──
    training_result = await db.execute(
        select(TrainingRecord)
        .where(TrainingRecord.passed == True)
    )
    all_training = training_result.scalars().all()

    # Build lookup: staff_id -> set of trained categories
    staff_trained_categories: dict[str, set] = {}
    for tr in all_training:
        staff_trained_categories.setdefault(tr.staff_id, set())
        if tr.service_category:
            staff_trained_categories[tr.staff_id].add(tr.service_category.lower())

    # Build lookup: location_id -> list of staff
    location_staff: dict[str, list] = {}
    for sp in all_staff:
        if sp.location_id:
            location_staff.setdefault(sp.location_id, []).append(sp)

    # ── Get locations ──
    loc_result = await db.execute(
        select(Location).where(Location.is_active == True)
    )
    locations = {loc.id: loc for loc in loc_result.scalars().all()}

    # ── Analyze each trend ──
    training_gaps = []
    for trend in trends:
        category = (trend.service_category or "").lower()
        if not category:
            continue

        signal = float(trend.overall_signal_strength) if trend.overall_signal_strength else 0
        branches_lacking = []
        total_staff_needing = 0

        for loc_id, staff_list in location_staff.items():
            loc = locations.get(loc_id)
            if not loc:
                continue

            untrained = []
            for sp in staff_list:
                trained_cats = staff_trained_categories.get(sp.id, set())
                if category not in trained_cats:
                    untrained.append(sp.id)

            if untrained:
                branches_lacking.append({
                    "location_id": loc_id,
                    "location_name": loc.name,
                    "city": loc.city,
                    "total_staff": len(staff_list),
                    "untrained_count": len(untrained),
                })
                total_staff_needing += len(untrained)

        if branches_lacking:
            urgency = "critical" if signal >= 7 else "high" if signal >= 5 else "medium"
            training_gaps.append({
                "trend_id": trend.id,
                "trend_name": trend.trend_name,
                "signal_strength": signal,
                "skill_needed": category,
                "branches_lacking": branches_lacking,
                "total_branches_affected": len(branches_lacking),
                "staff_needing_training": total_staff_needing,
                "recommended_training_program": f"{category.title()} Skills Workshop — {trend.trend_name}",
                "urgency": urgency,
                "training_actions": trend.training_actions,
            })

    # Sort by urgency
    urgency_order = {"critical": 0, "high": 1, "medium": 2}
    training_gaps.sort(key=lambda x: urgency_order.get(x["urgency"], 3))

    return APIResponse(
        success=True,
        data={
            "total_trends_with_gaps": len(training_gaps),
            "total_staff_needing_training": sum(g["staff_needing_training"] for g in training_gaps),
            "training_gaps": training_gaps,
        },
    )


trend_linked_training_agent = register_agent(AgentAction(
    name="trend_linked_training",
    description="Identify trends blocked by skill gaps — staff needing training per branch with urgency",
    track="trends",
    feature="training",
    method="get",
    path="/agents/track4/trends/linked-training",
    handler=trend_linked_training_handler,
    roles=["salon_manager", "regional_manager", "franchise_owner", "super_admin"],
    ps_codes=["PS-04.07"],
))


# ─────────────────────────────────────────────────────────────────────────────
# 41. competitor_intelligence  (PS-04.08)
# ─────────────────────────────────────────────────────────────────────────────

async def competitor_intelligence_handler(
    competitor_data: dict = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "regional_manager", "franchise_owner", "super_admin"])),
):
    """Store competitor intel and compare against Naturals' offerings."""

    if not competitor_data:
        raise HTTPException(status_code=400, detail="competitor_data is required")

    comp_name = competitor_data.get("competitor_name", "Unknown")
    city = competitor_data.get("city")
    services_offered = competitor_data.get("services_offered", [])
    price_range = competitor_data.get("price_range", {})
    promotions = competitor_data.get("promotions", [])

    # ── Store competitive intel ──
    intel = CompetitiveIntel(
        competitor_name=comp_name,
        intel_type="service_comparison",
        description=f"Services: {', '.join(services_offered[:10])}. Promotions: {', '.join(promotions[:5])}",
        city=city,
        relevance_score=0.8,
    )
    db.add(intel)
    await db.flush()

    # ── Get our services in that city ──
    our_services_query = select(Service.category, Service.name, Service.base_price).where(Service.is_active == True)
    our_result = await db.execute(our_services_query)
    our_services = our_result.all()

    our_categories = set()
    our_price_map: dict[str, list[float]] = {}
    for cat, name, price in our_services:
        if cat:
            our_categories.add(cat.lower())
            our_price_map.setdefault(cat.lower(), []).append(float(price))

    # ── Price comparison ──
    price_comparison = []
    comp_min = price_range.get("min")
    comp_max = price_range.get("max")
    for cat, prices in our_price_map.items():
        our_avg = sum(prices) / len(prices)
        entry = {
            "category": cat,
            "our_avg_price": round(our_avg, 2),
            "our_min": round(min(prices), 2),
            "our_max": round(max(prices), 2),
        }
        if comp_min is not None and comp_max is not None:
            comp_avg = (float(comp_min) + float(comp_max)) / 2
            entry["competitor_avg_price"] = comp_avg
            entry["price_difference_pct"] = round(((our_avg - comp_avg) / comp_avg) * 100, 1) if comp_avg > 0 else 0
            entry["position"] = "higher" if our_avg > comp_avg else "lower" if our_avg < comp_avg else "equal"
        price_comparison.append(entry)

    # ── Service gaps: what competitor offers that we don't ──
    comp_categories_lower = [s.lower() for s in services_offered]
    service_gaps = [s for s in comp_categories_lower if s not in our_categories]

    # ── Competitive advantages: what we have that they don't ──
    competitive_advantages = []
    competitive_advantages.append("SOULSKIN emotional beauty experience — unique to Naturals")
    competitive_advantages.append("AI-powered beauty diagnostics and digital twin")
    competitive_advantages.append("Personalized homecare plans with climate adjustments")
    # Check if we have more categories
    our_only = our_categories - set(comp_categories_lower)
    if our_only:
        competitive_advantages.append(f"Exclusive service categories: {', '.join(list(our_only)[:5])}")

    # ── Recommended actions ──
    recommended_actions = []
    if service_gaps:
        recommended_actions.append(f"Consider adding services: {', '.join(service_gaps[:5])}")
    if price_comparison:
        higher_priced = [p for p in price_comparison if p.get("position") == "higher"]
        if higher_priced:
            recommended_actions.append(
                f"Review pricing for {len(higher_priced)} categories where we are priced higher than {comp_name}"
            )
    if promotions:
        recommended_actions.append(f"Counter-promote against: {', '.join(promotions[:3])}")
    recommended_actions.append("Leverage SOULSKIN and AI differentiators in marketing")

    # Update intel record with action
    intel.action_recommended = "; ".join(recommended_actions[:3])

    return APIResponse(
        success=True,
        data={
            "intel_id": intel.id,
            "competitor_name": comp_name,
            "city": city,
            "services_compared": len(services_offered),
            "price_comparison": price_comparison,
            "service_gaps": service_gaps,
            "competitive_advantages": competitive_advantages,
            "recommended_actions": recommended_actions,
        },
    )


competitor_intelligence_agent = register_agent(AgentAction(
    name="competitor_intelligence",
    description="Store competitor data, compare prices and services, identify gaps and advantages",
    track="trends",
    feature="competitive",
    method="post",
    path="/agents/track4/competitive/intelligence",
    handler=competitor_intelligence_handler,
    roles=["salon_manager", "regional_manager", "franchise_owner", "super_admin"],
    ps_codes=["PS-04.08"],
    requires_ai=True,
))


async def competitive_listing_handler(
    city: str = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "regional_manager", "franchise_owner", "super_admin"])),
):
    """AI Agent: Retrieves stored competitive intelligence reports."""
    q = select(CompetitiveIntel).order_by(CompetitiveIntel.detected_at.desc())
    if city:
        q = q.where(CompetitiveIntel.city == city)
    
    result = await db.execute(q)
    intel_records = result.scalars().all()
    
    data = []
    for intel in intel_records:
        data.append({
            "id": str(intel.id),
            "competitor_name": intel.competitor_name,
            "city": intel.city,
            "type": intel.intel_type,
            "description": intel.description,
            "sentiment_score": intel.review_sentiment or 75,
            "distance_km": intel.distance_km or 1.2,
            "identified_advantage": intel.identified_advantage or "Premium SOULSKIN Experience",
            "top_feedback_summary": intel.top_feedback_summary or "High quality services, slightly higher wait times.",
            "avg_service_price": int(intel.avg_service_price or 1200),
            "detected_at": str(intel.detected_at) if intel.detected_at else None
        })
    
    return APIResponse(success=True, data=data)


competitive_listing_agent = register_agent(AgentAction(
    name="competitive_listing",
    description="List all stored competitive intelligence reports",
    track="trends",
    feature="competitive",
    method="get",
    path="/agents/track4/competitive/listing",
    handler=competitive_listing_handler,
    roles=["salon_manager", "regional_manager", "franchise_owner", "super_admin"],
    ps_codes=["PS-04.08"],
))


# ─────────────────────────────────────────────────────────────────────────────
# 42. product_launch_timing  (PS-04.09)
# ─────────────────────────────────────────────────────────────────────────────

async def product_launch_timing_handler(
    product_category: str = Query(..., description="e.g., keratin treatment, organic facial"),
    target_cities: list[str] = Query(default=[], description="Cities to target"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "regional_manager", "franchise_owner", "super_admin"])),
):
    """Analyze seasonal demand and trends to determine optimal product launch window."""

    now = datetime.now(timezone.utc)
    cat_lower = product_category.lower()

    # ── Monthly demand curves from historical bookings ──
    monthly_demand: dict[int, int] = {}
    for month_num in range(1, 13):
        result = await db.execute(
            select(func.count(Booking.id))
            .join(Service, Service.id == Booking.service_id)
            .where(
                Booking.status == BookingStatus.COMPLETED,
                extract("month", Booking.scheduled_at) == month_num,
                func.lower(Service.category) == cat_lower,
            )
        )
        count = result.scalar() or 0
        monthly_demand[month_num] = count

    # If target cities specified, also get city-specific data
    city_demand: dict[str, dict[int, int]] = {}
    if target_cities:
        for city in target_cities:
            city_monthly: dict[int, int] = {}
            for month_num in range(1, 13):
                result = await db.execute(
                    select(func.count(Booking.id))
                    .join(Service, Service.id == Booking.service_id)
                    .join(Location, Location.id == Booking.location_id)
                    .where(
                        Booking.status == BookingStatus.COMPLETED,
                        extract("month", Booking.scheduled_at) == month_num,
                        func.lower(Service.category) == cat_lower,
                        Location.city == city,
                    )
                )
                city_monthly[month_num] = result.scalar() or 0
            city_demand[city] = city_monthly

    # ── Find peak month ──
    if max(monthly_demand.values(), default=0) > 0:
        peak_month = max(monthly_demand, key=monthly_demand.get)
    else:
        # Default seasonal logic
        seasonal_peaks = {
            "hair color": 10,  # festive season
            "facial": 3,       # pre-summer
            "keratin": 6,      # pre-monsoon
            "bridal": 11,      # wedding season
            "de-tan": 4,       # summer start
            "hair spa": 1,     # winter care
        }
        peak_month = seasonal_peaks.get(cat_lower, 1)

    # Launch 1-2 months before peak
    launch_month = ((peak_month - 2) % 12) or 12

    # ── Competing trends ──
    competing_result = await db.execute(
        select(TrendSignal.trend_name, TrendSignal.overall_signal_strength, TrendSignal.predicted_peak_date)
        .where(
            TrendSignal.is_active == True,
            func.lower(TrendSignal.service_category) == cat_lower,
        )
        .order_by(desc(TrendSignal.overall_signal_strength))
        .limit(5)
    )
    competing_trends = [
        {
            "trend_name": row[0],
            "signal_strength": float(row[1]) if row[1] else 0,
            "predicted_peak": str(row[2]) if row[2] else None,
        }
        for row in competing_result.all()
    ]

    # ── Confidence score ──
    total_bookings = sum(monthly_demand.values())
    confidence = min(0.95, 0.3 + (total_bookings / max(total_bookings + 50, 1)) * 0.65)

    # ── Demand forecast for launch month ──
    month_names = [
        "", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    demand_forecast = [
        {"month": month_names[m], "month_number": m, "historical_bookings": monthly_demand.get(m, 0)}
        for m in range(1, 13)
    ]

    return APIResponse(
        success=True,
        data={
            "product_category": product_category,
            "target_cities": target_cities,
            "recommended_launch_month": month_names[launch_month],
            "recommended_launch_month_number": launch_month,
            "peak_demand_month": month_names[peak_month],
            "peak_demand_month_number": peak_month,
            "demand_forecast": demand_forecast,
            "competing_trends": competing_trends,
            "confidence_score": round(confidence, 2),
            "city_specific_data": {
                city: {
                    "peak_month": month_names[max(data, key=data.get)] if max(data.values(), default=0) > 0 else "Insufficient data",
                    "monthly_demand": data,
                }
                for city, data in city_demand.items()
            } if city_demand else None,
            "recommendation": f"Launch {product_category} in {month_names[launch_month]} to capture the {month_names[peak_month]} demand peak",
        },
    )


product_launch_timing_agent = register_agent(AgentAction(
    name="product_launch_timing",
    description="Determine optimal product/service launch timing based on seasonal demand and trend analysis",
    track="trends",
    feature="launch",
    method="post",
    path="/agents/track4/trends/product-launch-timing",
    handler=product_launch_timing_handler,
    roles=["salon_manager", "regional_manager", "franchise_owner", "super_admin"],
    ps_codes=["PS-04.09"],
))


# ─────────────────────────────────────────────────────────────────────────────
# 43. campaign_recommender  (PS-04.10)
# ─────────────────────────────────────────────────────────────────────────────

async def campaign_recommender_handler(
    month: Optional[int] = Query(None, ge=1, le=12, description="Target month (1-12)"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(["salon_manager", "regional_manager", "franchise_owner", "super_admin"])),
):
    """Recommend campaigns based on trends, underbooked categories, and customer behavior."""

    now = datetime.now(timezone.utc)
    target_month = month or now.month

    month_names = [
        "", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    # ── Trending services ──
    trend_result = await db.execute(
        select(TrendSignal)
        .where(TrendSignal.is_active == True, TrendSignal.overall_signal_strength > 4.0)
        .order_by(desc(TrendSignal.overall_signal_strength))
        .limit(5)
    )
    trending = trend_result.scalars().all()

    # ── Underbooked service categories (compare this month to average) ──
    current_bookings_result = await db.execute(
        select(Service.category, func.count(Booking.id).label("cnt"))
        .join(Booking, Booking.service_id == Service.id)
        .where(
            Booking.status.in_([BookingStatus.COMPLETED, BookingStatus.CONFIRMED]),
            extract("month", Booking.scheduled_at) == target_month,
            extract("year", Booking.scheduled_at) == now.year,
        )
        .group_by(Service.category)
    )
    current_bookings: dict[str, int] = {}
    for row in current_bookings_result.all():
        if row[0]:
            current_bookings[row[0]] = row[1]

    # Average monthly bookings per category (last 12 months)
    avg_result = await db.execute(
        select(
            Service.category,
            (func.count(Booking.id) / 12).label("avg_monthly"),
        )
        .join(Booking, Booking.service_id == Service.id)
        .where(
            Booking.status == BookingStatus.COMPLETED,
            Booking.scheduled_at >= now - timedelta(days=365),
        )
        .group_by(Service.category)
    )
    avg_bookings: dict[str, float] = {}
    for row in avg_result.all():
        if row[0]:
            avg_bookings[row[0]] = float(row[1]) if row[1] else 0

    underbooked = []
    for cat, avg in avg_bookings.items():
        current = current_bookings.get(cat, 0)
        if avg > 0 and current < avg * 0.7:
            underbooked.append({
                "category": cat,
                "current_bookings": current,
                "average_bookings": round(avg, 1),
                "deficit_pct": round(((avg - current) / avg) * 100, 1),
            })
    underbooked.sort(key=lambda x: x["deficit_pct"], reverse=True)

    # ── Customer segments with declining visit frequency ──
    # Customers who used to visit monthly but haven't in 45+ days
    declining_result = await db.execute(
        select(func.count(CustomerProfile.id))
        .where(
            CustomerProfile.total_visits > 3,
            CustomerProfile.last_visit_date < (date.today() - timedelta(days=45)),
        )
    )
    declining_customers = declining_result.scalar() or 0

    # ── Generate campaign recommendations ──
    campaigns = []

    # 1. Trend-riding campaign
    if trending:
        top_trend = trending[0]
        campaigns.append({
            "campaign_theme": f"Trending Now: {top_trend.trend_name}",
            "target_segment": "All customers, especially trend-seekers aged 18-35",
            "featured_services": [top_trend.service_category] if top_trend.service_category else ["Trending services"],
            "recommended_channel": "Instagram, WhatsApp",
            "predicted_response_rate": min(0.25, float(top_trend.overall_signal_strength or 0) / 40),
            "timing": f"Launch in {month_names[target_month]} — trend is {enum_val(top_trend.trajectory) if top_trend.trajectory else 'active'}",
            "rationale": f"Signal strength: {float(top_trend.overall_signal_strength or 0)}/10",
        })

    # 2. Underbooked category boost
    if underbooked:
        top_ub = underbooked[0]
        campaigns.append({
            "campaign_theme": f"{top_ub['category'].title()} Revival — Special Pricing",
            "target_segment": f"Customers who previously booked {top_ub['category']} services",
            "featured_services": [top_ub["category"]],
            "recommended_channel": "WhatsApp, SMS, Push Notification",
            "predicted_response_rate": 0.15,
            "timing": f"Immediate — {top_ub['deficit_pct']}% below average for {month_names[target_month]}",
            "rationale": f"Currently {top_ub['current_bookings']} bookings vs average {top_ub['average_bookings']}",
        })

    # 3. Win-back campaign
    if declining_customers > 0:
        campaigns.append({
            "campaign_theme": "We Miss You — Exclusive Return Offer",
            "target_segment": f"{declining_customers} customers who haven't visited in 45+ days",
            "featured_services": [top_cat for top_cat in list(avg_bookings.keys())[:3]],
            "recommended_channel": "WhatsApp, Email, SMS",
            "predicted_response_rate": 0.12,
            "timing": f"{month_names[target_month]} — personalized offers with 15% discount",
            "rationale": f"{declining_customers} previously active customers at risk of churn",
        })

    # 4. Seasonal campaign
    seasonal_themes = {
        1: ("New Year, New You", "Hair makeover + Skin refresh"),
        2: ("Valentine's Glow", "Couples packages, romantic styling"),
        3: ("Holi-Proof Beauty", "Pre-Holi hair protection, post-festival repair"),
        4: ("Summer Ready", "De-tan, sunscreen facial, frizz control"),
        5: ("Beat the Heat", "Cool scalp treatments, light styling"),
        6: ("Monsoon Prep", "Anti-frizz keratin, waterproof makeup lessons"),
        7: ("Monsoon Care", "Humidity protection, fungal scalp care"),
        8: ("Independence Glam", "Tricolor nail art, patriotic styling"),
        9: ("Navratri Looks", "Festive makeup, traditional hairstyles"),
        10: ("Diwali Dazzle", "Gold facial, festive makeup, mehndi"),
        11: ("Wedding Season", "Bridal packages, party styling"),
        12: ("Year-End Glow Up", "Annual beauty reset, gift vouchers"),
    }
    theme, details = seasonal_themes.get(target_month, ("Monthly Special", "Curated services"))
    campaigns.append({
        "campaign_theme": theme,
        "target_segment": "All customers",
        "featured_services": [details],
        "recommended_channel": "All channels — Instagram, WhatsApp, In-store",
        "predicted_response_rate": 0.18,
        "timing": f"Week 1 of {month_names[target_month]}",
        "rationale": f"Seasonal relevance for {month_names[target_month]}",
    })

    # 5. Loyalty tier upgrade push
    campaigns.append({
        "campaign_theme": "Level Up Your Loyalty",
        "target_segment": "Silver and Bronze tier customers close to next tier threshold",
        "featured_services": list(current_bookings.keys())[:3] if current_bookings else ["All services"],
        "recommended_channel": "Push Notification, WhatsApp",
        "predicted_response_rate": 0.20,
        "timing": f"Mid-{month_names[target_month]}",
        "rationale": "Incentivize tier upgrades to increase visit frequency and LTV",
    })

    return APIResponse(
        success=True,
        data={
            "target_month": month_names[target_month],
            "trending_services_count": len(trending),
            "underbooked_categories_count": len(underbooked),
            "declining_customers_count": declining_customers,
            "campaigns": campaigns,
            "underbooked_categories": underbooked[:5],
        },
    )


campaign_recommender_agent = register_agent(AgentAction(
    name="campaign_recommender",
    description="Recommend marketing campaigns based on trends, underbooked categories, and customer segments",
    track="trends",
    feature="campaign",
    method="get",
    path="/agents/track4/campaigns/recommend",
    handler=campaign_recommender_handler,
    roles=["salon_manager", "regional_manager", "franchise_owner", "super_admin"],
    ps_codes=["PS-04.10"],
))
