"""AURA Service Layer — Business logic for bookings, auth, analytics, SOULSKIN, quality, climate."""
from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Booking, BookingStatus, CustomerFeedback, SoulskinSession, ServiceSession


async def get_booking_stats(db: AsyncSession, location_id: UUID = None):
    """Aggregate booking stats for a location or network."""
    q = select(func.count(Booking.id), func.sum(Booking.final_price))
    if location_id:
        q = q.where(Booking.location_id == location_id)
    result = await db.execute(q)
    row = result.one()
    return {"total_bookings": row[0] or 0, "total_revenue": float(row[1] or 0)}


async def get_quality_stats(db: AsyncSession, location_id: UUID = None):
    """Average quality metrics."""
    q = select(func.avg(CustomerFeedback.overall_rating), func.count(CustomerFeedback.id))
    if location_id:
        q = q.where(CustomerFeedback.location_id == location_id)
    result = await db.execute(q)
    row = result.one()
    return {"avg_quality": round(float(row[0] or 0), 2), "total_reviews": row[1] or 0}


async def get_soulskin_stats(db: AsyncSession, location_id: UUID = None):
    """SOULSKIN session analytics."""
    q = select(func.count(SoulskinSession.id))
    if location_id:
        q = q.where(SoulskinSession.location_id == location_id)
    total = await db.scalar(q)

    q2 = select(func.count(SoulskinSession.id)).where(SoulskinSession.session_completed == True)
    if location_id:
        q2 = q2.where(SoulskinSession.location_id == location_id)
    completed = await db.scalar(q2)
    return {"total_sessions": total or 0, "completed": completed or 0, "completion_rate": round((completed or 0) / max(total or 1, 1) * 100, 1)}
