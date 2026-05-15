"""CRUD — Services domain."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.service import Service


async def get_by_id(db: AsyncSession, service_id: str) -> Service | None:
    result = await db.execute(
        select(Service).where(Service.id == service_id, Service.is_deleted == False)
    )
    return result.scalar_one_or_none()


async def list_active(db: AsyncSession, category: str | None = None) -> list[Service]:
    q = select(Service).where(Service.is_active == True, Service.is_deleted == False)
    if category:
        q = q.where(Service.category == category)
    result = await db.execute(q)
    return list(result.scalars().all())


async def create(db: AsyncSession, data: dict) -> Service:
    service = Service(**data)
    db.add(service)
    await db.flush()
    return service


async def update(db: AsyncSession, service: Service, data: dict) -> Service:
    for k, v in data.items():
        setattr(service, k, v)
    await db.flush()
    return service
