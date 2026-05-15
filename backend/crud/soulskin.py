"""CRUD — SOULSKIN sessions domain."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.soulskin import SoulskinSession


async def get_by_id(db: AsyncSession, session_id: str) -> SoulskinSession | None:
    result = await db.execute(select(SoulskinSession).where(SoulskinSession.id == session_id))
    return result.scalar_one_or_none()


async def get_by_customer(db: AsyncSession, customer_id: str, limit: int = 20) -> list[SoulskinSession]:
    result = await db.execute(
        select(SoulskinSession)
        .where(SoulskinSession.customer_id == customer_id)
        .order_by(SoulskinSession.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_by_booking(db: AsyncSession, booking_id: str) -> SoulskinSession | None:
    result = await db.execute(
        select(SoulskinSession).where(SoulskinSession.booking_id == booking_id)
    )
    return result.scalar_one_or_none()


async def create(db: AsyncSession, data: dict) -> SoulskinSession:
    session = SoulskinSession(**data)
    db.add(session)
    await db.flush()
    return session


async def update(db: AsyncSession, session: SoulskinSession, data: dict) -> SoulskinSession:
    for k, v in data.items():
        setattr(session, k, v)
    await db.flush()
    return session
