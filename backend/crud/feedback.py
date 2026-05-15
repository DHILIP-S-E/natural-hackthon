"""CRUD — Feedback domain."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.feedback import CustomerFeedback


async def get_by_booking(db: AsyncSession, booking_id: str) -> CustomerFeedback | None:
    result = await db.execute(
        select(CustomerFeedback).where(CustomerFeedback.booking_id == booking_id)
    )
    return result.scalar_one_or_none()


async def get_by_location(db: AsyncSession, location_id: str, limit: int = 100) -> list[CustomerFeedback]:
    result = await db.execute(
        select(CustomerFeedback)
        .where(CustomerFeedback.location_id == location_id)
        .order_by(CustomerFeedback.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def create(db: AsyncSession, data: dict) -> CustomerFeedback:
    fb = CustomerFeedback(**data)
    db.add(fb)
    await db.flush()
    return fb
