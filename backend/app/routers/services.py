"""Services & SOPs router."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db, enum_val
from app.models.user import User
from app.models.service import Service, SOP
from app.dependencies import get_current_user
from app.schemas.common import APIResponse

router = APIRouter(prefix="/services", tags=["Services & SOPs"])


@router.get("", response_model=APIResponse)
async def list_services(
    category: Optional[str] = None,
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all services."""
    query = select(Service)
    if active_only:
        query = query.where(Service.is_active == True)
    if category:
        query = query.where(Service.category == category)

    result = await db.execute(query.order_by(Service.category, Service.name).limit(200))
    services = result.scalars().all()

    return APIResponse(success=True, data=[
        {
            "id": s.id, "name": s.name, "category": s.category,
            "subcategory": s.subcategory, "short_description": s.short_description,
            "duration_minutes": s.duration_minutes,
            "base_price": float(s.base_price) if s.base_price else None,
            "skill_required": enum_val(s.skill_required) if s.skill_required else None,
            "is_chemical": s.is_chemical, "ar_preview_available": s.ar_preview_available,
            "tags": s.tags, "image_url": s.image_url,
        }
        for s in services
    ])


@router.get("/{service_id}", response_model=APIResponse)
async def get_service(
    service_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get service details with SOP."""
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # Get SOP
    sop_data = None
    if service.sop_id:
        sop_result = await db.execute(select(SOP).where(SOP.id == service.sop_id))
        sop = sop_result.scalar_one_or_none()
        if sop:
            sop_data = {
                "id": sop.id, "title": sop.title, "version": sop.version,
                "steps": sop.steps, "soulskin_overlays": sop.soulskin_overlays,
                "products_required": sop.products_required,
                "chemicals_involved": sop.chemicals_involved,
                "chemical_ratios": sop.chemical_ratios,
                "total_duration_minutes": sop.total_duration_minutes,
            }

    return APIResponse(success=True, data={
        "id": service.id, "name": service.name, "category": service.category,
        "description": service.description, "duration_minutes": service.duration_minutes,
        "base_price": float(service.base_price), "is_chemical": service.is_chemical,
        "tags": service.tags, "sop": sop_data,
    })
