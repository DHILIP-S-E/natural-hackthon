"""CRUD — Locations domain."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.location import Location


async def get_by_id(db: AsyncSession, location_id: str) -> Location | None:
    result = await db.execute(
        select(Location).where(Location.id == location_id, Location.is_deleted == False)
    )
    return result.scalar_one_or_none()


async def list_active(db: AsyncSession) -> list[Location]:
    result = await db.execute(
        select(Location).where(Location.is_active == True, Location.is_deleted == False)
    )
    return list(result.scalars().all())


async def list_all(db: AsyncSession, limit: int = 200) -> list[Location]:
    result = await db.execute(
        select(Location).where(Location.is_deleted == False).limit(limit)
    )
    return list(result.scalars().all())


async def create(db: AsyncSession, data: dict) -> Location:
    location = Location(**data)
    db.add(location)
    await db.flush()
    return location


async def update(db: AsyncSession, location: Location, data: dict) -> Location:
    for k, v in data.items():
        setattr(location, k, v)
    await db.flush()
    return location
