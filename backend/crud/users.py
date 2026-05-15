"""CRUD — Users domain."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.user import User


async def get_by_id(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    return result.scalar_one_or_none()


async def get_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(
        select(User).where(User.email == email, User.is_deleted == False)
    )
    return result.scalar_one_or_none()


async def list_by_role(db: AsyncSession, role: str, limit: int = 100) -> list[User]:
    result = await db.execute(
        select(User).where(User.role == role, User.is_deleted == False).limit(limit)
    )
    return list(result.scalars().all())


async def create(db: AsyncSession, data: dict) -> User:
    user = User(**data)
    db.add(user)
    await db.flush()
    return user


async def update(db: AsyncSession, user: User, data: dict) -> User:
    for k, v in data.items():
        setattr(user, k, v)
    await db.flush()
    return user


async def soft_delete(db: AsyncSession, user: User) -> None:
    user.is_deleted = True
    await db.flush()
