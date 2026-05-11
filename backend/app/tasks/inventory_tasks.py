"""Inventory Tasks — Feature 9: Demand forecasting + WhatsApp alerts to managers.

Beat schedule:
- Stockout check: Daily at 7:00 AM IST
- Festival demand spike alerts: Weekly on Sundays at 8:00 AM IST
"""
import asyncio
from datetime import datetime, timezone, timedelta, date
from app.tasks.celery_app import celery_app
from app.database import async_session_factory


# Indian festival calendar — hardcoded major events, admin can add regional via DB
# Format: (month, day, name, demand_multiplier)
FESTIVAL_CALENDAR = [
    (1, 14, "Pongal / Makar Sankranti", 1.8),
    (1, 26, "Republic Day", 1.2),
    (2, 14, "Valentine's Day", 1.5),
    (3, 8, "Women's Day", 1.6),
    (3, 25, "Holi", 1.4),
    (4, 14, "Tamil New Year / Vishu / Baisakhi", 1.7),
    (8, 15, "Independence Day", 1.3),
    (8, 26, "Onam Season Start", 1.6),
    (10, 2, "Gandhi Jayanti", 1.1),
    (10, 15, "Navratri Season", 1.9),
    (10, 24, "Dussehra", 1.8),
    (11, 1, "Diwali Season", 2.2),
    (11, 12, "Diwali", 2.5),
    (12, 24, "Christmas Eve", 1.6),
    (12, 25, "Christmas", 1.5),
    (12, 31, "New Year's Eve", 2.0),
]

LOW_STOCK_MESSAGE = (
    "⚠️ Low Stock Alert — {location_name}\n"
    "{product_name} has only {current_stock} {unit} remaining "
    "(predicted {days_until_stockout} days until stockout). "
    "Recommended order: {suggested_order} {unit}. Please place order with your supplier."
)

FESTIVAL_ALERT_MESSAGE = (
    "📅 Festival Demand Alert — {location_name}\n"
    "{festival_name} is {days_away} days away (demand x{multiplier}). "
    "Consider stocking up on: {top_products}. "
    "Review your inventory now: https://natural.dhilip.in/manager/inventory"
)


def _get_upcoming_festivals(days_ahead: int = 14) -> list:
    """Return festivals occurring within the next N days."""
    today = date.today()
    upcoming = []
    for month, day, name, multiplier in FESTIVAL_CALENDAR:
        try:
            festival_date = date(today.year, month, day)
        except ValueError:
            continue
        days_away = (festival_date - today).days
        if 0 <= days_away <= days_ahead:
            upcoming.append({
                "name": name,
                "date": festival_date.isoformat(),
                "days_away": days_away,
                "multiplier": multiplier,
            })
    return upcoming


@celery_app.task(name="app.tasks.inventory_tasks.check_low_stock")
def check_low_stock():
    """Daily check: alert managers for items below reorder level or < 2x weekly usage."""
    async def _run():
        async with async_session_factory() as db:
            from sqlalchemy import select
            from app.models.inventory import InventoryItem
            from app.models.location import Location
            from app.models.user import User
            from app.services.sns_service import send_whatsapp

            result = await db.execute(
                select(InventoryItem).where(
                    InventoryItem.current_stock <= InventoryItem.reorder_level,
                )
            )
            low_items = result.scalars().all()

            # Group by location to send one message per manager
            location_alerts: dict[str, list] = {}
            for item in low_items:
                loc_id = str(item.location_id)
                if loc_id not in location_alerts:
                    location_alerts[loc_id] = []
                location_alerts[loc_id].append(item)

            for loc_id, items in location_alerts.items():
                location = await db.get(Location, loc_id)
                if not location or not location.manager_id:
                    continue

                mgr_r = await db.execute(select(User).where(User.id == location.manager_id))
                mgr = mgr_r.scalar_one_or_none()
                if not mgr or not mgr.phone:
                    continue

                for item in items[:5]:  # Max 5 alerts per message to avoid spam
                    daily_usage = item.average_daily_usage or 1
                    days_until = max(0, int(item.current_stock / daily_usage)) if daily_usage > 0 else 99
                    suggested_order = max(
                        item.reorder_level * 3,
                        int(daily_usage * 30),  # 30-day supply
                    )

                    msg = LOW_STOCK_MESSAGE.format(
                        location_name=location.name,
                        product_name=item.product_name,
                        current_stock=item.current_stock,
                        unit=item.unit_of_measure or "units",
                        days_until_stockout=days_until,
                        suggested_order=suggested_order,
                    )
                    await send_whatsapp(mgr.phone, msg)

            await db.commit()

    return asyncio.run(_run())


@celery_app.task(name="app.tasks.inventory_tasks.send_festival_demand_alerts")
def send_festival_demand_alerts():
    """Weekly: alert managers about upcoming festivals and predicted demand spikes."""
    async def _run():
        async with async_session_factory() as db:
            from sqlalchemy import select
            from app.models.location import Location
            from app.models.user import User
            from app.models.inventory import InventoryItem
            from app.services.sns_service import send_whatsapp

            upcoming = _get_upcoming_festivals(days_ahead=14)
            if not upcoming:
                return

            locations_result = await db.execute(
                select(Location).where(Location.is_active == True)
            )
            locations = locations_result.scalars().all()

            for loc in locations:
                if not loc.manager_id:
                    continue

                mgr_r = await db.execute(select(User).where(User.id == loc.manager_id))
                mgr = mgr_r.scalar_one_or_none()
                if not mgr or not mgr.phone:
                    continue

                # Get top products likely to spike during festivals
                items_r = await db.execute(
                    select(InventoryItem)
                    .where(InventoryItem.location_id == loc.id)
                    .order_by(InventoryItem.average_daily_usage.desc())
                    .limit(3)
                )
                top_items = items_r.scalars().all()
                top_products = ", ".join(i.product_name for i in top_items) or "hair colour, keratin, facial products"

                for festival in upcoming[:2]:  # Alert for max 2 upcoming festivals
                    msg = FESTIVAL_ALERT_MESSAGE.format(
                        location_name=loc.name,
                        festival_name=festival["name"],
                        days_away=festival["days_away"],
                        multiplier=festival["multiplier"],
                        top_products=top_products,
                    )
                    await send_whatsapp(mgr.phone, msg)

    return asyncio.run(_run())


@celery_app.task(name="app.tasks.inventory_tasks.get_festival_calendar")
def get_festival_calendar_task():
    """Utility task: return the festival calendar (used by the frontend API)."""
    return {"festivals": FESTIVAL_CALENDAR}
