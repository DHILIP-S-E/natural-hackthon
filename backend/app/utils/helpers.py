"""Helper utilities."""
import uuid
from datetime import datetime, timezone


def generate_booking_number() -> str:
    """Generate a unique booking number like BK-2026-000001."""
    now = datetime.now(timezone.utc)
    short_id = uuid.uuid4().hex[:6].upper()
    return f"BK-{now.year}-{short_id}"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
