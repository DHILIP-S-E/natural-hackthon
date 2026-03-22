"""Trends router — Social listening, demand forecasting."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, enum_val
from app.dependencies import get_current_user
from app.models import TrendSignal
from app.schemas.common import APIResponse

router = APIRouter(prefix="/trends", tags=["Trends"])


@router.get("/", response_model=APIResponse)
async def list_trends(city: str = None, category: str = None,
                      db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    q = select(TrendSignal).where(TrendSignal.is_active == True).order_by(TrendSignal.overall_signal_strength.desc())
    if category:
        q = q.where(TrendSignal.service_category == category)
    result = await db.execute(q)
    trends = result.scalars().all()
    data = []
    for t in trends:
        if city and t.applicable_cities and city not in t.applicable_cities:
            continue
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
