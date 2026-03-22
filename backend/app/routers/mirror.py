"""AR Mirror router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db, enum_val
from app.dependencies import get_current_user
from app.models import ARMirrorSession
from app.schemas.common import APIResponse

router = APIRouter(prefix="/mirror", tags=["AR Mirror"])


@router.get("/", response_model=APIResponse)
async def list_sessions(customer_id: UUID = None, location_id: UUID = None,
                        db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    q = select(ARMirrorSession).order_by(ARMirrorSession.created_at.desc()).limit(20)
    if customer_id:
        q = q.where(ARMirrorSession.customer_id == customer_id)
    if location_id:
        q = q.where(ARMirrorSession.location_id == location_id)
    result = await db.execute(q)
    sessions = result.scalars().all()
    return APIResponse(success=True, data=[{
        "id": str(s.id), "session_type": enum_val(s.session_type) if s.session_type else None,
        "saved_images": s.saved_images or [],
    } for s in sessions])


@router.post("/", response_model=APIResponse)
async def create_session(
    customer_id: UUID, location_id: UUID, session_type: str = "hairstyle_try_on",
    db: AsyncSession = Depends(get_db), user=Depends(get_current_user),
):
    session = ARMirrorSession(
        customer_id=customer_id, location_id=location_id,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return APIResponse(success=True, data={"id": str(session.id)}, message="Mirror session created")
