"""CRUD — Staff domain."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from models.staff import StaffProfile


async def get_by_id(db: AsyncSession, staff_id: str) -> StaffProfile | None:
    result = await db.execute(
        select(StaffProfile).where(StaffProfile.id == staff_id, StaffProfile.is_deleted == False)
    )
    return result.scalar_one_or_none()


async def get_by_location(db: AsyncSession, location_id: str) -> list[StaffProfile]:
    result = await db.execute(
        select(StaffProfile).where(
            and_(StaffProfile.location_id == location_id, StaffProfile.is_deleted == False)
        )
    )
    return list(result.scalars().all())


async def get_available(db: AsyncSession, location_id: str) -> list[StaffProfile]:
    result = await db.execute(
        select(StaffProfile).where(
            and_(
                StaffProfile.location_id == location_id,
                StaffProfile.is_available == True,
                StaffProfile.is_deleted == False,
            )
        )
    )
    return list(result.scalars().all())


async def create(db: AsyncSession, data: dict) -> StaffProfile:
    staff = StaffProfile(**data)
    db.add(staff)
    await db.flush()
    return staff


async def update(db: AsyncSession, staff: StaffProfile, data: dict) -> StaffProfile:
    for k, v in data.items():
        setattr(staff, k, v)
    await db.flush()
    return staff
