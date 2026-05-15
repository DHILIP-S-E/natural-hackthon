"""CRUD — Notifications domain."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from models.notification import Notification


async def get_by_user(db: AsyncSession, user_id: str, unread_only: bool = False, limit: int = 50) -> list[Notification]:
    q = select(Notification).where(Notification.user_id == user_id)
    if unread_only:
        q = q.where(Notification.is_read == False)
    q = q.order_by(Notification.created_at.desc()).limit(limit)
    result = await db.execute(q)
    return list(result.scalars().all())


async def mark_read(db: AsyncSession, notification_id: str) -> bool:
    result = await db.execute(select(Notification).where(Notification.id == notification_id))
    notif = result.scalar_one_or_none()
    if not notif:
        return False
    notif.is_read = True
    await db.flush()
    return True


async def create(db: AsyncSession, data: dict) -> Notification:
    notif = Notification(**data)
    db.add(notif)
    await db.flush()
    return notif
