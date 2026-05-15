"""Notifications router — Multi-channel notification management."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, timezone

from db.db import get_db, enum_val
from utils.dependencies import get_current_user
from models import Notification
from schemas.common import APIResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/", response_model=APIResponse)
async def list_notifications(page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100),
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


@router.post("/webhook/whatsapp-reply", response_model=APIResponse)
async def whatsapp_reply_webhook(body: dict):
    """Inbound WhatsApp reply webhook (SNS / Twilio callback).
    Routes NPS score replies to nps_tasks.process_nps_reply.
    Body expected: { "from": "+91...", "text": "8" }
    """
    phone = body.get("from") or body.get("phone") or ""
    text = (body.get("text") or body.get("body") or "").strip()
    if not phone or not text:
        return APIResponse(success=False, message="Missing phone or text")

    # Try to parse as NPS reply (numeric 1-10)
    try:
        score = int(text.split()[0])
        if 1 <= score <= 10:
            from tasks.nps_tasks import process_nps_reply
            process_nps_reply.delay(phone, text)
            return APIResponse(success=True, message="NPS reply queued", data={"score": score})
    except (ValueError, IndexError):
        pass

    # Otherwise route to chatbot
    return APIResponse(success=True, message="Reply received — not an NPS score")
