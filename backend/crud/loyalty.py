"""CRUD — Loyalty domain."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.loyalty import LoyaltyProfile, LoyaltyTransaction


async def get_profile_by_customer(db: AsyncSession, customer_id: str) -> LoyaltyProfile | None:
    result = await db.execute(
        select(LoyaltyProfile).where(LoyaltyProfile.customer_id == customer_id)
    )
    return result.scalar_one_or_none()


async def get_transactions(db: AsyncSession, customer_id: str, limit: int = 50) -> list[LoyaltyTransaction]:
    result = await db.execute(
        select(LoyaltyTransaction)
        .where(LoyaltyTransaction.customer_id == customer_id)
        .order_by(LoyaltyTransaction.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def create_profile(db: AsyncSession, data: dict) -> LoyaltyProfile:
    profile = LoyaltyProfile(**data)
    db.add(profile)
    await db.flush()
    return profile


async def create_transaction(db: AsyncSession, data: dict) -> LoyaltyTransaction:
    tx = LoyaltyTransaction(**data)
    db.add(tx)
    await db.flush()
    return tx


async def update_profile(db: AsyncSession, profile: LoyaltyProfile, data: dict) -> LoyaltyProfile:
    for k, v in data.items():
        setattr(profile, k, v)
    await db.flush()
    return profile
