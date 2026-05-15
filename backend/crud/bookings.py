"""CRUD — Bookings domain. DB reads/writes only, no business logic."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from models.booking import Booking


async def get_by_id(db: AsyncSession, booking_id: str) -> Booking | None:
    result = await db.execute(select(Booking).where(Booking.id == booking_id, Booking.is_deleted == False))
    return result.scalar_one_or_none()


async def get_by_customer(db: AsyncSession, customer_id: str, limit: int = 50) -> list[Booking]:
    result = await db.execute(
        select(Booking)
        .where(and_(Booking.customer_id == customer_id, Booking.is_deleted == False))
        .order_by(Booking.scheduled_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_by_location(db: AsyncSession, location_id: str, limit: int = 100) -> list[Booking]:
    result = await db.execute(
        select(Booking)
        .where(and_(Booking.location_id == location_id, Booking.is_deleted == False))
        .order_by(Booking.scheduled_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def create(db: AsyncSession, data: dict) -> Booking:
    booking = Booking(**data)
    db.add(booking)
    await db.flush()
    return booking


async def update(db: AsyncSession, booking: Booking, data: dict) -> Booking:
    for k, v in data.items():
        setattr(booking, k, v)
    await db.flush()
    return booking


async def soft_delete(db: AsyncSession, booking: Booking) -> None:
    booking.is_deleted = True
    await db.flush()
