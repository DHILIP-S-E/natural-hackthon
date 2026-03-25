"""Trends router — Social listening, demand forecasting."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, enum_val
from app.dependencies import get_current_user
from app.models import TrendSignal, User
from app.schemas.common import APIResponse
from app.agents.track4_trends import (
    trend_early_detection_handler,
    predictive_inventory_handler,
    regional_trend_map_handler,
    celebrity_trend_alert_handler,
    seasonal_demand_forecast_handler,
    social_trend_ingest_handler,
    trend_linked_training_handler,
    competitor_intelligence_handler,
    product_launch_timing_handler,
    campaign_recommender_handler
)

router = APIRouter(prefix="/trends", tags=["Trends"])


@router.get("/", response_model=APIResponse)
async def list_trends(city: str = None, category: str = None, limit: int = 100, offset: int = 0,
                      db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    from sqlalchemy import cast, String
    q = select(TrendSignal).where(TrendSignal.is_active == True).order_by(TrendSignal.overall_signal_strength.desc())
    if category:
        q = q.where(TrendSignal.service_category == category)
    # Filter city in SQL instead of Python to avoid loading all rows
    if city:
        q = q.where(
            TrendSignal.applicable_cities.is_(None) |
            cast(TrendSignal.applicable_cities, String).contains(city)
        )
    result = await db.execute(q.offset(offset).limit(limit))
    trends = result.scalars().all()
    data = []
    for t in trends:
        data.append({
            "id": str(t.id), "trend_name": t.trend_name, "slug": t.slug,
            "description": t.description, "service_category": t.service_category,
            "signal_strength": t.overall_signal_strength, "social_media_score": t.social_media_score,
            "search_trend_score": t.search_trend_score, "booking_demand_score": t.booking_demand_score,
            "trajectory": enum_val(t.trajectory) if t.trajectory else None,
            "longevity": enum_val(t.longevity_label) if t.longevity_label else None,
            "confidence": t.confidence_level, "applicable_cities": t.applicable_cities,
            "celebrity_trigger": t.celebrity_trigger,
        })
    return APIResponse(success=True, data=data)


@router.get("/{trend_id}", response_model=APIResponse)
async def get_trend(trend_id: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    from uuid import UUID
    trend = await db.get(TrendSignal, UUID(trend_id))
    if not trend:
        from fastapi import HTTPException
        raise HTTPException(404, "Trend not found")
    return APIResponse(success=True, data={
        "id": str(trend.id), "trend_name": trend.trend_name, "description": trend.description,
        "signal_strength": trend.overall_signal_strength,
        "trajectory": enum_val(trend.trajectory) if trend.trajectory else None,
        "climate_correlation": trend.climate_correlation,
    })


@router.get("/agents/early-detection", response_model=APIResponse)
async def get_early_trend_detection(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """AI Agent: Scans social, search, and bookings for early trend signals."""
    return await trend_early_detection_handler(db, user)


@router.get("/agents/inventory-prediction", response_model=APIResponse)
async def get_inventory_prediction(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """AI Agent: Predicts inventory needs based on trending services."""
    return await predictive_inventory_handler(db, user)


@router.get("/agents/regional-map", response_model=APIResponse)
async def get_regional_trend_map(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """AI Agent: Generates a heatmap of service demand across regions."""
    return await regional_trend_map_handler(db, user)


@router.get("/agents/celebrity-radar", response_model=APIResponse)
async def get_celebrity_trend_radar(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """AI Agent: Monitors celebrity style changes and alerts of emerging trends."""
    return await celebrity_trend_alert_handler(db, user)


@router.get("/agents/seasonal-forecast", response_model=APIResponse)
async def get_seasonal_forecast(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """AI Agent: Forecasts seasonal service demand trends."""
    return await seasonal_demand_forecast_handler(db, user)


@router.get("/agents/training-gaps", response_model=APIResponse)
async def get_trend_training_gaps(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """AI Agent: Identifies skill gaps preventing adoption of new trends."""
    return await trend_linked_training_handler(db, user)

@router.get("/agents/launch-timing", response_model=APIResponse)
async def get_product_launch_timing(
    product_category: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """AI Agent: Recommends optimal timing for new product/service launches."""
    return await product_launch_timing_handler(product_category, [], db, user)


@router.get("/agents/campaigns", response_model=APIResponse)
async def get_campaign_recommendations(
    month: int = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """AI Agent: Recommends marketing campaigns based on trends and demand."""
    return await campaign_recommender_handler(month, db, user)
