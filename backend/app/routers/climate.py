"""Climate router — Weather-based beauty recommendations with live API integration."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models import ClimateRecommendation
from app.schemas.common import APIResponse

router = APIRouter(prefix="/climate", tags=["Climate"])


@router.get("/", response_model=APIResponse)
async def get_climate(city: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    """Get climate recommendations for a city. Auto-fetches if stale or missing."""
    from app.services.weather_service import get_or_refresh_climate

    try:
        rec = await get_or_refresh_climate(city, db)
    except Exception:
        # Fallback: try DB only
        result = await db.execute(
            select(ClimateRecommendation)
            .where(ClimateRecommendation.city == city)
            .order_by(ClimateRecommendation.date_for.desc())
            .limit(1)
        )
        rec = result.scalar_one_or_none()

    if not rec:
        return APIResponse(success=True, data=None, message=f"No climate data for {city}")
    return APIResponse(success=True, data={
        "city": rec.city, "date_for": str(rec.date_for),
        "temperature": float(rec.temperature_celsius) if rec.temperature_celsius else None,
        "humidity": float(rec.humidity_pct) if rec.humidity_pct else None,
        "uv_index": float(rec.uv_index) if rec.uv_index else None,
        "aqi": float(rec.aqi) if rec.aqi else None,
        "weather_condition": rec.weather_condition, "is_alert": rec.is_alert,
        "hair_recommendations": rec.hair_recommendations,
        "skin_recommendations": rec.skin_recommendations,
        "general_advisory": rec.general_advisory,
    })


@router.get("/alerts", response_model=APIResponse)
async def get_climate_alerts(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(
        select(ClimateRecommendation)
        .where(ClimateRecommendation.is_alert == True, ClimateRecommendation.date_for >= date.today())
        .order_by(ClimateRecommendation.date_for)
        .limit(100)
    )
    alerts = result.scalars().all()
    return APIResponse(success=True, data=[{
        "city": a.city, "date_for": str(a.date_for),
        "uv_index": float(a.uv_index) if a.uv_index else None,
        "aqi": float(a.aqi) if a.aqi else None,
        "hair_recommendations": a.hair_recommendations,
        "skin_recommendations": a.skin_recommendations,
        "general_advisory": a.general_advisory,
    } for a in alerts])


@router.get("/{city}/forecast", response_model=APIResponse)
async def get_climate_forecast(city: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    """Get 7-day beauty forecast for a city."""
    from datetime import timedelta
    today = date.today()
    result = await db.execute(
        select(ClimateRecommendation)
        .where(
            ClimateRecommendation.city == city,
            ClimateRecommendation.date_for >= today,
            ClimateRecommendation.date_for <= today + timedelta(days=7),
        )
        .order_by(ClimateRecommendation.date_for)
    )
    forecasts = result.scalars().all()
    return APIResponse(success=True, data=[{
        "date": str(f.date_for),
        "temperature": float(f.temperature_celsius) if f.temperature_celsius else None,
        "humidity": float(f.humidity_pct) if f.humidity_pct else None,
        "uv_index": float(f.uv_index) if f.uv_index else None,
        "aqi": float(f.aqi) if f.aqi else None,
        "weather_condition": f.weather_condition,
        "is_alert": f.is_alert,
        "hair_recommendations": f.hair_recommendations,
        "skin_recommendations": f.skin_recommendations,
    } for f in forecasts])


@router.post("/sync", response_model=APIResponse)
async def refresh_climate(
    city: str = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(["salon_manager", "super_admin"])),
):
    """Force refresh climate data for a city or all active cities."""
    from app.services.weather_service import fetch_and_store_climate
    from app.models.location import Location

    cities_refreshed = []
    if city:
        cities = [city]
    else:
        result = await db.execute(
            select(Location.city).where(Location.is_active == True).distinct()
        )
        cities = [row[0] for row in result.all() if row[0]]

    # Use asyncio.gather for parallel HTTP calls instead of sequential loop
    import asyncio

    async def _refresh_one(c: str) -> str:
        try:
            await fetch_and_store_climate(c, db)
            return c
        except Exception as e:
            return f"{c} (failed: {str(e)[:50]})"

    cities_refreshed = await asyncio.gather(*[_refresh_one(c) for c in cities])

    return APIResponse(success=True, data={"cities_refreshed": list(cities_refreshed)}, message=f"Refreshed {len(cities_refreshed)} cities")
