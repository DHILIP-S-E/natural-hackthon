"""SOPs router — Standard Operating Procedure management."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models import SOP
from app.schemas.common import APIResponse

router = APIRouter(prefix="/sops", tags=["SOPs"])


@router.get("/", response_model=APIResponse)
async def list_sops(service_id: UUID = None, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    q = select(SOP).order_by(SOP.created_at.desc())
    if service_id:
        q = q.where(SOP.service_id == service_id)
    result = await db.execute(q)
    sops = result.scalars().all()
    return APIResponse(success=True, data=[{
        "id": str(s.id), "title": s.title, "version": s.version,
        "total_duration_minutes": s.total_duration_minutes,
        "chemicals_involved": s.chemicals_involved,
        "step_count": len(s.steps) if s.steps else 0,
    } for s in sops])


@router.get("/{sop_id}", response_model=APIResponse)
async def get_sop(sop_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    sop = await db.get(SOP, sop_id)
    if not sop:
        raise HTTPException(404, "SOP not found")
    return APIResponse(success=True, data={
        "id": str(sop.id), "title": sop.title, "version": sop.version,
        "total_duration_minutes": sop.total_duration_minutes,
        "chemicals_involved": sop.chemicals_involved,
        "chemical_ratios": sop.chemical_ratios,
        "products_required": sop.products_required,
        "steps": sop.steps, "soulskin_overlays": sop.soulskin_overlays,
    })


@router.post("/", response_model=APIResponse)
async def create_sop(
    service_id: UUID, title: str, version: str = "1.0",
    total_duration_minutes: int = 60, chemicals_involved: bool = False,
    steps: list = None, soulskin_overlays: dict = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(["salon_manager", "super_admin"])),
):
    sop = SOP(
        service_id=service_id, title=title, version=version,
        total_duration_minutes=total_duration_minutes,
        chemicals_involved=chemicals_involved,
        steps=steps or [], soulskin_overlays=soulskin_overlays or {},
        created_by=user.id,
    )
    db.add(sop)
    await db.commit()
    await db.refresh(sop)
    return APIResponse(success=True, data={"id": str(sop.id)}, message="SOP created")
