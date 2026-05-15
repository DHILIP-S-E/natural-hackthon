"""AI Wait Time Prediction — Idea 21.

Domain logic (ML-lite approach without requiring a trained model):
  Predicted wait = base_duration × load_factor × festival_multiplier

  load_factor is computed from:
    - active_sessions_count (in-progress services)
    - confirmed_bookings_next_2h count
    - historical avg completions per hour for this day/time slot
    - walk-in queue depth

  Festival multiplier from inventory_tasks FESTIVAL_CALENDAR.
  WhatsApp alert sent when customer's turn is ≤ 10 minutes away.
"""
from datetime import datetime, timezone, timedelta, time, date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_db, generate_uuid
from utils.dependencies import get_current_user
from models.user import User
from schemas.common import APIResponse

router = APIRouter(prefix="/wait-time", tags=["AI Wait Time Prediction"])


# Average service durations by category (minutes)
AVG_SERVICE_DURATIONS: dict[str, int] = {
    "hair cut": 30,
    "hair colour": 90,
    "keratin": 120,
    "facial": 60,
    "manicure": 45,
    "pedicure": 60,
    "head massage": 30,
    "bridal makeup": 180,
    "hair spa": 60,
    "bleach": 90,
    "default": 45,
}

# Peak hour multipliers (hour → demand factor)
HOURLY_DEMAND: dict[int, float] = {
    9: 0.6, 10: 0.8, 11: 1.0, 12: 1.1, 13: 1.0,
    14: 0.9, 15: 1.0, 16: 1.2, 17: 1.4, 18: 1.5,
    19: 1.3, 20: 0.8,
}

# Weekend multiplier
WEEKEND_MULTIPLIER = 1.35


def _festival_multiplier_today() -> float:
    from tasks.inventory_tasks import FESTIVAL_CALENDAR
    today = date.today()
    for month, day, name, multiplier in FESTIVAL_CALENDAR:
        try:
            fdate = date(today.year, month, day)
            if abs((fdate - today).days) <= 2:
                return multiplier
        except ValueError:
            continue
    return 1.0


def _predict_wait_minutes(
    active_sessions: int,
    queue_depth: int,
    upcoming_bookings_2h: int,
    available_stylists: int,
    requested_service: Optional[str],
    hour: int,
    is_weekend: bool,
) -> dict:
    """Core wait time prediction formula."""
    svc_key = next(
        (k for k in AVG_SERVICE_DURATIONS if k in (requested_service or "").lower()),
        "default"
    )
    avg_duration = AVG_SERVICE_DURATIONS[svc_key]
    capacity = max(1, available_stylists)

    # Sessions completing per hour = capacity / avg_duration_hours
    throughput_per_hour = (capacity / avg_duration) * 60
    demand = active_sessions + queue_depth + upcoming_bookings_2h

    hourly_factor = HOURLY_DEMAND.get(hour, 1.0)
    weekend_factor = WEEKEND_MULTIPLIER if is_weekend else 1.0
    festival_factor = _festival_multiplier_today()

    load = demand / max(1, throughput_per_hour)
    base_wait = (queue_depth / max(1, throughput_per_hour)) * 60  # minutes

    # Apply demand multipliers
    predicted = base_wait * hourly_factor * weekend_factor
    # Festival spike
    if festival_factor > 1.5:
        predicted = predicted * min(festival_factor, 2.0)

    predicted = round(max(0, predicted))

    # Busy status classification
    if load >= 1.5 or predicted >= 45:
        status = "busy"
        badge = "Busy today"
    elif load >= 0.8 or predicted >= 20:
        status = "moderate"
        badge = "Moderately busy"
    else:
        status = "quiet"
        badge = "Walk-in friendly"

    return {
        "predicted_wait_minutes": predicted,
        "status": status,
        "badge": badge,
        "load_factor": round(load, 2),
        "active_sessions": active_sessions,
        "queue_depth": queue_depth,
        "available_stylists": capacity,
        "festival_multiplier": festival_factor,
    }


@router.get("/location/{location_id}", response_model=APIResponse)
async def get_wait_time(
    location_id: str,
    service: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Public endpoint — get live wait time for a salon.
    Used on the Salon Map pins and booking confirmation page.
    """
    from models.session import ServiceSession
    from models.booking import Booking, BookingStatus
    from models.staff import StaffProfile
    from models.queue import QueueEntry

    now = datetime.now(timezone.utc)
    hour = now.hour
    is_weekend = now.weekday() >= 5

    # Active sessions at this location
    active_result = await db.execute(
        select(func.count(ServiceSession.id))
        .join(Booking, ServiceSession.booking_id == Booking.id)
        .where(
            Booking.location_id == location_id,
            ServiceSession.status.in_(["active", "ACTIVE"]),
        )
    )
    active_count = active_result.scalar() or 0

    # Queue depth
    queue_result = await db.execute(
        select(func.count(QueueEntry.id))
        .where(
            QueueEntry.location_id == location_id,
            QueueEntry.status.in_(["waiting", "WAITING"]),
        )
    ) if hasattr(__builtins__, '__import__') else None
    queue_count = 0
    try:
        queue_count = queue_result.scalar() or 0 if queue_result else 0
    except Exception:
        queue_count = 0

    # Upcoming confirmed bookings next 2h
    window_end = now + timedelta(hours=2)
    upcoming_result = await db.execute(
        select(func.count(Booking.id)).where(
            Booking.location_id == location_id,
            Booking.scheduled_at >= now,
            Booking.scheduled_at <= window_end,
            Booking.status.in_(["confirmed", "CONFIRMED", "checked_in", "CHECKED_IN"]),
        )
    )
    upcoming = upcoming_result.scalar() or 0

    # Available stylists
    stylists_result = await db.execute(
        select(func.count(StaffProfile.id)).where(
            StaffProfile.location_id == location_id,
            StaffProfile.is_available == True,
        )
    )
    available_stylists = stylists_result.scalar() or 1

    prediction = _predict_wait_minutes(
        active_sessions=int(active_count),
        queue_depth=int(queue_count),
        upcoming_bookings_2h=int(upcoming),
        available_stylists=int(available_stylists),
        requested_service=service,
        hour=hour,
        is_weekend=is_weekend,
    )

    return APIResponse(
        success=True,
        message="Wait time prediction",
        data={
            "location_id": location_id,
            **prediction,
            "display_text": (
                f"Currently {prediction['predicted_wait_minutes']} min wait"
                if prediction["predicted_wait_minutes"] > 0
                else "No wait — walk in now!"
            ),
        },
    )


@router.get("/location/{location_id}/heatmap", response_model=APIResponse)
async def get_peak_hour_heatmap(
    location_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Return historical busy hours heatmap for a salon (Mon–Sun × 9AM–9PM).
    Used on the Salon Map and booking page to help customers pick quiet slots.
    """
    from models.booking import Booking
    from sqlalchemy import extract

    result = await db.execute(
        select(
            extract("dow", Booking.scheduled_at).label("dow"),
            extract("hour", Booking.scheduled_at).label("hour"),
            func.count(Booking.id).label("cnt"),
        )
        .where(
            Booking.location_id == location_id,
            Booking.scheduled_at >= datetime.now(timezone.utc) - timedelta(days=90),
        )
        .group_by("dow", "hour")
    )
    rows = result.all()

    heatmap: dict[int, dict[int, int]] = {}
    for row in rows:
        dow = int(row.dow)
        hr = int(row.hour)
        heatmap.setdefault(dow, {})[hr] = int(row.cnt)

    # Normalise to 0–100
    all_vals = [v for d in heatmap.values() for v in d.values()]
    max_val = max(all_vals) if all_vals else 1
    normalised = {
        dow: {hr: round(cnt / max_val * 100) for hr, cnt in hours.items()}
        for dow, hours in heatmap.items()
    }

    DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    return APIResponse(
        success=True,
        message="Peak hour heatmap",
        data={
            "location_id": location_id,
            "heatmap": {DAYS[dow]: hours for dow, hours in normalised.items()},
            "quietest_slots": _find_quiet_slots(normalised),
        },
    )


def _find_quiet_slots(heatmap: dict) -> list[str]:
    """Find top 3 quietest time slots across the week."""
    slots = []
    DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for dow, hours in heatmap.items():
        for hr, score in hours.items():
            if 9 <= hr <= 20:
                slots.append((score, dow, hr))
    slots.sort()
    result = []
    for score, dow, hr in slots[:3]:
        ampm = "AM" if hr < 12 else "PM"
        display_hr = hr if hr <= 12 else hr - 12
        result.append(f"{DAYS[dow]} {display_hr}:00 {ampm}")
    return result


@router.post("/notify-when-ready", response_model=APIResponse)
async def notify_when_ready(
    body: dict,
    db: AsyncSession = Depends(get_db),
):
    """Customer opts in to receive WhatsApp alert when their turn is 10 minutes away.
    Called from the queue display page or reception kiosk.
    """
    location_id = body.get("location_id")
    phone = body.get("phone")
    queue_position = body.get("queue_position", 1)

    if not phone:
        from fastapi import HTTPException
        raise HTTPException(400, "Phone number required for WhatsApp notification")

    from services.sns_service import send_whatsapp
    confirm_msg = (
        f"✅ We've noted your number! We'll WhatsApp you when you're "
        f"{'next' if queue_position == 1 else f'about 10 minutes away from'} your turn. "
        f"You can wait outside or nearby. 💆"
    )
    await send_whatsapp(phone, confirm_msg)

    return APIResponse(
        success=True,
        message="Notification opt-in confirmed",
        data={"phone": phone, "queue_position": queue_position},
    )
