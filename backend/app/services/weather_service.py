"""AURA Weather Service — OpenWeatherMap integration with beauty recommendations."""
import json
from datetime import date, datetime, timezone, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.climate import ClimateRecommendation
from app.database import generate_uuid

# ── City coordinates for demo locations (fallback when Location model lacks lat/lng) ──
_CITY_COORDS = {
    "chennai": (13.0827, 80.2707),
    "bangalore": (12.9716, 77.5946),
    "mumbai": (19.0760, 72.8777),
    "delhi": (28.6139, 77.2090),
    "hyderabad": (17.3850, 78.4867),
    "coimbatore": (11.0168, 76.9558),
    "pune": (18.5204, 73.8567),
    "kolkata": (22.5726, 88.3639),
}

# ── Beauty recommendation thresholds ──
_THRESHOLDS = {
    "uv_critical": 8,
    "uv_high": 6,
    "humidity_high": 75,
    "humidity_low": 30,
    "temp_hot": 35,
    "temp_cold": 15,
    "aqi_poor": 150,
    "aqi_bad": 200,
}


def _derive_beauty_recs(temp_c: float, humidity: float, uv: float, aqi: float, condition: str) -> dict:
    """Pure function: weather data → beauty recommendation dicts."""
    hair_alerts = []
    hair_tips = []
    skin_alerts = []
    skin_tips = []

    # UV-based
    if uv >= _THRESHOLDS["uv_critical"]:
        hair_alerts.append(f"Critical UV ({uv:.1f}) — recommend UV-protective gloss finish on all services")
        skin_alerts.append(f"UV Index {uv:.1f} — apply SPF 50+ before and after service")
        skin_tips.append("Double SPF application. Reapply every 2 hours outdoors.")
    elif uv >= _THRESHOLDS["uv_high"]:
        hair_alerts.append(f"High UV ({uv:.1f}) — suggest leave-in UV protection spray")
        skin_alerts.append(f"UV Index {uv:.1f} — recommend SPF 30+ application")

    # Humidity-based
    if humidity >= _THRESHOLDS["humidity_high"]:
        hair_alerts.append(f"High humidity ({humidity:.0f}%) — avoid keratin services today, recommend anti-frizz serum")
        hair_tips.append("Apply lightweight anti-frizz serum before stepping out")
    elif humidity <= _THRESHOLDS["humidity_low"]:
        hair_alerts.append(f"Low humidity ({humidity:.0f}%) — hair is prone to static and dryness")
        hair_tips.append("Use a hydrating leave-in conditioner")

    # Temperature-based
    if temp_c >= _THRESHOLDS["temp_hot"]:
        skin_tips.append("Stay hydrated. Avoid heavy moisturizers — use gel-based formulas")
        hair_tips.append("Minimize heat styling — natural air dry recommended")
    elif temp_c <= _THRESHOLDS["temp_cold"]:
        skin_tips.append("Use richer moisturizers. Protect lips and hands from cold wind")
        hair_tips.append("Deep conditioning recommended — cold air strips moisture")

    # AQI-based
    if aqi >= _THRESHOLDS["aqi_bad"]:
        skin_alerts.append(f"Poor air quality (AQI {aqi:.0f}) — recommend deep cleansing facial")
        hair_alerts.append(f"High pollution (AQI {aqi:.0f}) — scalp detox treatment advised")
    elif aqi >= _THRESHOLDS["aqi_poor"]:
        skin_tips.append("Antioxidant serum recommended to combat pollution damage")

    # Weather condition
    if "rain" in condition.lower():
        hair_tips.append("Humidity will rise — apply anti-frizz before leaving salon")

    is_alert = uv >= _THRESHOLDS["uv_critical"] or aqi >= _THRESHOLDS["aqi_bad"] or humidity >= _THRESHOLDS["humidity_high"]

    return {
        "hair_recommendations": {
            "alerts": hair_alerts,
            "service_adjustments": hair_alerts[:2],
            "home_care_tip": hair_tips[0] if hair_tips else "Maintain your regular hair care routine today",
        },
        "skin_recommendations": {
            "alerts": skin_alerts,
            "service_adjustments": skin_alerts[:2],
            "home_care_tip": skin_tips[0] if skin_tips else "SPF and hydration as usual",
        },
        "general_advisory": f"Temperature {temp_c:.1f}°C | Humidity {humidity:.0f}% | UV {uv:.1f} | AQI {aqi:.0f} — {'Take extra precautions today' if is_alert else 'Normal conditions for beauty services'}",
        "is_alert": is_alert,
    }


def _fallback_climate(city: str) -> dict:
    """Synthetic climate data when OWM API is unavailable."""
    # India-typical defaults by region
    defaults = {
        "chennai": {"temp": 32, "humidity": 78, "uv": 9.2, "aqi": 142, "condition": "Partly Cloudy"},
        "bangalore": {"temp": 26, "humidity": 55, "uv": 7.5, "aqi": 95, "condition": "Cloudy"},
        "mumbai": {"temp": 30, "humidity": 82, "uv": 8.0, "aqi": 168, "condition": "Hazy"},
        "delhi": {"temp": 28, "humidity": 45, "uv": 8.5, "aqi": 220, "condition": "Hazy"},
    }
    d = defaults.get(city.lower(), {"temp": 28, "humidity": 60, "uv": 7.0, "aqi": 100, "condition": "Clear"})
    return d


async def _fetch_open_meteo(city: str) -> dict:
    """Fetch weather from Open-Meteo (FREE, no API key required)."""
    import aiohttp

    coords = _CITY_COORDS.get(city.lower())
    if not coords:
        raise RuntimeError(f"No coordinates for city: {city}")

    lat, lon = coords
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,weather_code,uv_index"
        f"&timezone=Asia/Kolkata"
    )

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Open-Meteo returned {resp.status}")
            data = await resp.json()

    current = data.get("current", {})
    temp_c = current.get("temperature_2m", 28)
    humidity = current.get("relative_humidity_2m", 60)
    uv = current.get("uv_index", 5.0)
    weather_code = current.get("weather_code", 0)

    # Map WMO weather codes to conditions
    if weather_code == 0:
        condition = "Clear"
    elif weather_code <= 3:
        condition = "Partly Cloudy"
    elif weather_code <= 49:
        condition = "Foggy"
    elif weather_code <= 69:
        condition = "Rainy"
    elif weather_code <= 79:
        condition = "Snowy"
    elif weather_code <= 99:
        condition = "Thunderstorm"
    else:
        condition = "Cloudy"

    # Open-Meteo doesn't provide AQI — estimate from city defaults
    aqi_defaults = {"chennai": 142, "bangalore": 95, "mumbai": 168, "delhi": 220,
                    "hyderabad": 130, "coimbatore": 80, "pune": 110, "kolkata": 180}
    aqi = aqi_defaults.get(city.lower(), 100)

    return {"temp": temp_c, "humidity": humidity, "uv": uv, "aqi": aqi, "condition": condition}


async def _fetch_owm(city: str) -> dict:
    """Fetch weather data from OpenWeatherMap API."""
    import aiohttp

    base = getattr(settings, 'OPENWEATHER_BASE_URL', 'https://api.openweathermap.org/data/2.5')
    api_key = settings.OPENWEATHER_API_KEY

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
        weather_url = f"{base}/weather?q={city},IN&appid={api_key}&units=metric"
        async with session.get(weather_url) as resp:
            if resp.status != 200:
                raise RuntimeError(f"OWM weather API returned {resp.status}")
            weather = await resp.json()

        temp_c = weather.get("main", {}).get("temp", 28)
        humidity = weather.get("main", {}).get("humidity", 60)
        condition = weather.get("weather", [{}])[0].get("main", "Clear")
        lat = weather.get("coord", {}).get("lat", 0)
        lon = weather.get("coord", {}).get("lon", 0)

        uv = 5.0
        try:
            uv_url = f"{base}/uvi?lat={lat}&lon={lon}&appid={api_key}"
            async with session.get(uv_url) as uv_resp:
                if uv_resp.status == 200:
                    uv_data = await uv_resp.json()
                    uv = uv_data.get("value", 5.0)
        except Exception:
            coords = _CITY_COORDS.get(city.lower())
            if coords:
                uv = 7.0 + (coords[0] - 15) * 0.2

        aqi = 100.0
        try:
            aqi_url = f"{base}/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
            async with session.get(aqi_url) as aqi_resp:
                if aqi_resp.status == 200:
                    aqi_data = await aqi_resp.json()
                    aqi_list = aqi_data.get("list", [])
                    if aqi_list:
                        components = aqi_list[0].get("components", {})
                        aqi = components.get("pm2_5", 50) * 2
        except Exception:
            pass

    return {"temp": temp_c, "humidity": humidity, "uv": uv, "aqi": aqi, "condition": condition}


async def fetch_and_store_climate(city: str, db: AsyncSession) -> ClimateRecommendation:
    """Fetch weather, derive beauty recs, upsert to DB. Tries Open-Meteo (free) → OWM → fallback."""
    try:
        # First try Open-Meteo (free, no key needed)
        weather = await _fetch_open_meteo(city)
    except Exception:
        try:
            if settings.OPENWEATHER_API_KEY:
                weather = await _fetch_owm(city)
            else:
                weather = _fallback_climate(city)
        except Exception:
            weather = _fallback_climate(city)

    recs = _derive_beauty_recs(
        weather["temp"], weather["humidity"], weather["uv"], weather["aqi"], weather["condition"]
    )

    today = date.today()
    now = datetime.now(timezone.utc)

    # Upsert: check if row exists for this city+date
    result = await db.execute(
        select(ClimateRecommendation).where(
            ClimateRecommendation.city == city,
            ClimateRecommendation.date_for == today,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.temperature_celsius = weather["temp"]
        existing.humidity_pct = weather["humidity"]
        existing.uv_index = weather["uv"]
        existing.aqi = weather["aqi"]
        existing.weather_condition = weather["condition"]
        existing.hair_recommendations = recs["hair_recommendations"]
        existing.skin_recommendations = recs["skin_recommendations"]
        existing.general_advisory = recs["general_advisory"]
        existing.is_alert = recs["is_alert"]
        existing.fetched_at = now
        return existing
    else:
        rec = ClimateRecommendation(
            id=generate_uuid(),
            city=city,
            date_for=today,
            fetched_at=now,
            temperature_celsius=weather["temp"],
            humidity_pct=weather["humidity"],
            uv_index=weather["uv"],
            aqi=weather["aqi"],
            weather_condition=weather["condition"],
            hair_recommendations=recs["hair_recommendations"],
            skin_recommendations=recs["skin_recommendations"],
            general_advisory=recs["general_advisory"],
            is_alert=recs["is_alert"],
        )
        db.add(rec)
        await db.flush()
        return rec


async def get_or_refresh_climate(city: str, db: AsyncSession, max_age_hours: int = 6) -> Optional[ClimateRecommendation]:
    """Get climate data, refreshing if stale."""
    today = date.today()
    result = await db.execute(
        select(ClimateRecommendation).where(
            ClimateRecommendation.city == city,
            ClimateRecommendation.date_for == today,
        )
    )
    existing = result.scalar_one_or_none()

    if existing and existing.fetched_at:
        fetched = existing.fetched_at
        if fetched.tzinfo is None:
            fetched = fetched.replace(tzinfo=timezone.utc)
        age = datetime.now(timezone.utc) - fetched
        if age < timedelta(hours=max_age_hours):
            return existing

    return await fetch_and_store_climate(city, db)
