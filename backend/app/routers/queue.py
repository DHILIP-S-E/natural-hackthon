"""Queue router — Smart walk-in queue management."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, timezone

from app.database import get_db, enum_val
from app.dependencies import get_current_user, require_role
from app.models import SmartQueueEntry, QueueStatus, WalkInSource
from app.schemas.common import APIResponse

router = APIRouter(prefix="/queue", tags=["Queue"])


async def _smart_wait_estimate(location_id: str, service_id: str = None, db: AsyncSession = None) -> int:
    """Smart queue wait time estimation based on current sessions and service durations."""
    from app.models.service import Service

    # Get all WAITING and IN_SERVICE entries for this location
    result = await db.execute(
        select(SmartQueueEntry).where(
            SmartQueueEntry.location_id == location_id,
            SmartQueueEntry.status.in_([QueueStatus.WAITING, QueueStatus.IN_SERVICE,
                                         "waiting", "in_service"]),
        ).order_by(SmartQueueEntry.position_in_queue)
    )
    entries = result.scalars().all()

    # Batch-fetch all service durations to avoid N+1
    all_service_ids = list({e.service_id for e in entries if e.service_id})
    if service_id and service_id not in all_service_ids:
        all_service_ids.append(service_id)
    svc_durations: dict[str, int] = {}
    if all_service_ids:
        svc_result = await db.execute(
            select(Service.id, Service.duration_minutes).where(Service.id.in_(all_service_ids))
        )
        svc_durations = {row[0]: row[1] or 30 for row in svc_result.all()}

    total_wait = 0
    for e in entries:
        svc_dur = svc_durations.get(e.service_id, 30) if e.service_id else 30

        status = enum_val(e.status) if hasattr(e.status, 'value') else str(e.status)
        if status == "in_service" and e.service_started_at:
            elapsed = (datetime.now(timezone.utc) - e.service_started_at).total_seconds() / 60
            remaining = max(svc_dur - elapsed, 2)
            total_wait += int(remaining)
        elif status == "waiting":
            total_wait += svc_dur + 3  # 3-min buffer for handover

    # Add this customer's service duration
    if service_id:
        total_wait += svc_durations.get(service_id, 0)

    return max(total_wait, 0)


@router.get("/{location_id}", response_model=APIResponse)
async def get_queue(location_id: UUID, db: AsyncSession = Depends(get_db),
                    user=Depends(get_current_user)):
    result = await db.execute(
        select(SmartQueueEntry)
        .where(SmartQueueEntry.location_id == str(location_id),
               SmartQueueEntry.status.in_([QueueStatus.WAITING, QueueStatus.ASSIGNED, QueueStatus.IN_SERVICE]))
        .order_by(SmartQueueEntry.position_in_queue)
    )
    entries = result.scalars().all()
    return APIResponse(success=True, data=[{
        "id": str(e.id), "customer_name": e.customer_name,
        "customer_phone": e.customer_phone,
        "customer_id": e.customer_id,
        "service_id": e.service_id,
        "preferred_stylist_id": e.preferred_stylist_id,
        "position_in_queue": e.position_in_queue,
        "status": enum_val(e.status),
        "estimated_wait_mins": e.estimated_wait_mins,
        "actual_wait_mins": e.actual_wait_mins,
        "walk_in_source": enum_val(e.walk_in_source) if e.walk_in_source else None,
        "joined_queue_at": str(e.joined_queue_at) if e.joined_queue_at else None,
        "notes": e.notes,
    } for e in entries])


@router.post("/{location_id}/join", response_model=APIResponse)
async def join_queue(
    location_id: UUID,
    customer_name: str, customer_phone: str,
    service_id: UUID = None, preferred_stylist_id: UUID = None,
    walk_in_source: str = "in_person",
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    count = await db.scalar(
        select(func.count()).where(
            SmartQueueEntry.location_id == str(location_id),
            SmartQueueEntry.status == QueueStatus.WAITING
        )
    )
    try:
        source = WalkInSource(walk_in_source)
    except ValueError:
        source = WalkInSource.IN_PERSON

    entry = SmartQueueEntry(
        location_id=str(location_id),
        customer_name=customer_name,
        customer_phone=customer_phone,
        service_id=str(service_id) if service_id else None,
        preferred_stylist_id=str(preferred_stylist_id) if preferred_stylist_id else None,
        position_in_queue=(count or 0) + 1,
        status=QueueStatus.WAITING,
        estimated_wait_mins=await _smart_wait_estimate(str(location_id), str(service_id) if service_id else None, db),
        walk_in_source=source,
        joined_queue_at=datetime.now(timezone.utc),
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return APIResponse(success=True, data={
        "id": str(entry.id), "position_in_queue": entry.position_in_queue,
        "estimated_wait_mins": entry.estimated_wait_mins,
    }, message="Added to queue")


@router.patch("/{location_id}/{entry_id}", response_model=APIResponse)
async def update_queue_entry(location_id: UUID, entry_id: UUID,
                             status: str = None, notes: str = None,
                             db: AsyncSession = Depends(get_db),
                             user=Depends(require_role(["salon_manager", "stylist", "super_admin"]))):
    entry = await db.get(SmartQueueEntry, str(entry_id))
    if not entry:
        raise HTTPException(404, "Queue entry not found")
    if status:
        entry.status = QueueStatus(status)
        if status == "in_service":
            entry.service_started_at = datetime.now(timezone.utc)
        elif status == "completed":
            entry.service_completed_at = datetime.now(timezone.utc)
    if notes:
        entry.notes = notes
    await db.commit()
    return APIResponse(success=True, message="Queue entry updated")


@router.post("/{location_id}/{entry_id}/assign", response_model=APIResponse)
async def assign_stylist(location_id: UUID, entry_id: UUID, stylist_id: UUID,
                         db: AsyncSession = Depends(get_db),
                         user=Depends(require_role(["salon_manager", "super_admin"]))):
    entry = await db.get(SmartQueueEntry, str(entry_id))
    if not entry:
        raise HTTPException(404, "Queue entry not found")
    entry.status = QueueStatus.ASSIGNED
    entry.preferred_stylist_id = str(stylist_id)
    entry.assigned_at = datetime.now(timezone.utc)
    await db.commit()
    return APIResponse(success=True, message="Stylist assigned")


@router.post("/{location_id}/{entry_id}/notify", response_model=APIResponse)
async def notify_customer(location_id: UUID, entry_id: UUID,
                          db: AsyncSession = Depends(get_db),
                          user=Depends(require_role(["salon_manager", "stylist", "super_admin"]))):
    entry = await db.get(SmartQueueEntry, str(entry_id))
    if not entry:
        raise HTTPException(404, "Queue entry not found")
    entry.notified_by_whatsapp = True
    entry.notification_sent_at = datetime.now(timezone.utc)
    entry.notification_message = "Your stylist is ready! Please proceed to the salon."
    await db.commit()
    return APIResponse(success=True, message="Customer notified")


@router.get("/{location_id}/wait-estimate", response_model=APIResponse)
async def wait_estimate(location_id: UUID, service_id: str = None,
                        db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    count = await db.scalar(
        select(func.count()).where(
            SmartQueueEntry.location_id == str(location_id),
            SmartQueueEntry.status == QueueStatus.WAITING
        )
    )
    smart_wait = await _smart_wait_estimate(str(location_id), service_id, db)
    return APIResponse(success=True, data={
        "waiting_count": count or 0,
        "estimated_wait_mins": smart_wait,
    })


@router.delete("/{location_id}/{entry_id}", response_model=APIResponse)
async def remove_from_queue(location_id: UUID, entry_id: UUID,
                            db: AsyncSession = Depends(get_db),
                            user=Depends(get_current_user)):
    entry = await db.get(SmartQueueEntry, str(entry_id))
    if not entry:
        raise HTTPException(404, "Queue entry not found")
    entry.status = QueueStatus.LEFT
    await db.commit()
    return APIResponse(success=True, message="Removed from queue")
