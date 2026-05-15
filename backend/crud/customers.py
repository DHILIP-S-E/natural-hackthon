"""CRUD — Customers domain."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.customer import CustomerProfile


async def get_by_id(db: AsyncSession, customer_id: str) -> CustomerProfile | None:
    result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.id == customer_id, CustomerProfile.is_deleted == False)
    )
    return result.scalar_one_or_none()


async def get_by_user_id(db: AsyncSession, user_id: str) -> CustomerProfile | None:
    result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.user_id == user_id, CustomerProfile.is_deleted == False)
    )
    return result.scalar_one_or_none()


async def list_all(db: AsyncSession, limit: int = 100, offset: int = 0) -> list[CustomerProfile]:
    result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.is_deleted == False).limit(limit).offset(offset)
    )
    return list(result.scalars().all())


async def create(db: AsyncSession, data: dict) -> CustomerProfile:
    customer = CustomerProfile(**data)
    db.add(customer)
    await db.flush()
    return customer


async def update(db: AsyncSession, customer: CustomerProfile, data: dict) -> CustomerProfile:
    for k, v in data.items():
        setattr(customer, k, v)
    await db.flush()
    return customer
