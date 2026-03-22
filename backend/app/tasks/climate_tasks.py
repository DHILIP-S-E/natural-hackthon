"""AURA Climate Tasks — Periodic weather data refresh."""
import asyncio
from app.tasks.celery_app import celery_app
from app.database import async_session_factory


@celery_app.task(name="app.tasks.climate_tasks.refresh_all_cities_climate")
def refresh_all_cities_climate():
    """Refresh climate data for all active location cities. Runs every 6 hours via Celery Beat."""
    async def _run():
        async with async_session_factory() as db:
            from sqlalchemy import select
            from app.models.location import Location
            from app.services.weather_service import fetch_and_store_climate

            result = await db.execute(
                select(Location.city).where(Location.is_active == True).distinct()
            )
            cities = [row[0] for row in result.all() if row[0]]
            refreshed = []

            for city in cities:
                try:
                    await fetch_and_store_climate(city, db)
                    refreshed.append(city)
                except Exception as e:
                    print(f"[Climate Task] Failed for {city}: {e}")

            await db.commit()
            return {"refreshed": refreshed, "total": len(refreshed)}

    return asyncio.run(_run())
