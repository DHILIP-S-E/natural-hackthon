"""Notifications router — Multi-channel notification management."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, timezone

from app.database import get_db, enum_val
from app.dependencies import get_current_user
from app.models import Notification
from app.schemas.common import APIResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/", response_model=APIResponse)
async def list_notifications(page: int = 1, per_page: int = 20,
                             db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
        .offset((page - 1) * per_page).limit(per_page)
    )
    notifs = result.scalars().all()
    return APIResponse(success=True, data=[{
        "id": str(n.id), "title": n.title, "body": n.body,
        "notification_type": n.notification_type,
        "channel": enum_val(n.channel) if n.channel else None,
        "priority": enum_val(n.priority) if n.priority else None,
        "is_read": n.is_read, "data": n.data,
        "sent_at": str(n.sent_at) if n.sent_at else None,
        "created_at": str(n.created_at) if n.created_at else None,
    } for n in notifs])


@router.get("/unread-count", response_model=APIResponse)
async def unread_count(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    count = await db.scalar(
        select(func.count()).where(Notification.user_id == user.id, Notification.is_read == False)
    )
    return APIResponse(success=True, data={"unread_count": count or 0})


@router.patch("/{notif_id}/read", response_model=APIResponse)
async def mark_read(notif_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    notif = await db.get(Notification, str(notif_id))
    if not notif or notif.user_id != user.id:
        raise HTTPException(404, "Notification not found")
    notif.is_read = True
    notif.read_at = datetime.now(timezone.utc)
    await db.commit()
    return APIResponse(success=True, message="Marked as read")


@router.patch("/read-all", response_model=APIResponse)
async def mark_all_read(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    await db.execute(
        update(Notification).where(Notification.user_id == user.id, Notification.is_read == False)
        .values(is_read=True, read_at=datetime.now(timezone.utc))
    )
    await db.commit()
    return APIResponse(success=True, message="All notifications marked as read")
