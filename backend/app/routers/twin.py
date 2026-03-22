"""Digital Beauty Twin router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, timezone

from app.database import get_db
from app.dependencies import get_current_user
from app.models import DigitalBeautyTwin
from app.schemas.common import APIResponse

router = APIRouter(prefix="/twin", tags=["Digital Beauty Twin"])


@router.get("/{customer_id}", response_model=APIResponse)
async def get_twin(customer_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(
        select(DigitalBeautyTwin).where(DigitalBeautyTwin.customer_id == str(customer_id))
    )
    twin = result.scalar_one_or_none()
    if not twin:
        return APIResponse(success=True, data=None, message="No digital twin found")
    return APIResponse(success=True, data={
        "id": str(twin.id), "customer_id": twin.customer_id,
        "model_data_url": twin.model_data_url,
        "texture_url": twin.texture_url,
        "last_rebuilt_at": str(twin.last_rebuilt_at) if twin.last_rebuilt_at else None,
        "skin_timeline": twin.skin_timeline,
        "future_simulations": twin.future_simulations,
        "hairstyle_tryons": twin.hairstyle_tryons,
        "consent_given": twin.consent_given,
        "is_active": twin.is_active,
    })


@router.post("/", response_model=APIResponse)
async def create_twin(
    customer_id: UUID, model_data_url: str = None, texture_url: str = None,
    consent_given: bool = False,
    db: AsyncSession = Depends(get_db), user=Depends(get_current_user),
):
    # Check if twin already exists
    existing = await db.execute(
        select(DigitalBeautyTwin).where(DigitalBeautyTwin.customer_id == str(customer_id))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(409, "Digital twin already exists for this customer")
    twin = DigitalBeautyTwin(
        customer_id=str(customer_id),
        model_data_url=model_data_url,
        texture_url=texture_url,
        consent_given=consent_given,
        consent_date=datetime.now(timezone.utc) if consent_given else None,
        skin_timeline=[], future_simulations=[], hairstyle_tryons=[],
        is_active=True,
    )
    db.add(twin)
    await db.commit()
    await db.refresh(twin)
    return APIResponse(success=True, data={"id": str(twin.id)}, message="Digital twin created")


@router.post("/{customer_id}/rebuild", response_model=APIResponse)
async def rebuild_twin(customer_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(
        select(DigitalBeautyTwin).where(DigitalBeautyTwin.customer_id == str(customer_id))
    )
    twin = result.scalar_one_or_none()
    if not twin:
        raise HTTPException(404, "Digital twin not found")
    twin.last_rebuilt_at = datetime.now(timezone.utc)
    await db.commit()
    return APIResponse(success=True, message="Digital twin rebuild triggered")


@router.post("/{customer_id}/simulate", response_model=APIResponse)
async def simulate_future(customer_id: UUID, weeks_ahead: int = 12,
                          db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(
        select(DigitalBeautyTwin).where(DigitalBeautyTwin.customer_id == str(customer_id))
    )
    twin = result.scalar_one_or_none()
    if not twin:
        raise HTTPException(404, "Digital twin not found")
    simulations = twin.future_simulations or []
    simulations.append({
        "simulation_id": f"sim_{len(simulations)+1:03d}",
        "simulated_at": datetime.now(timezone.utc).isoformat(),
        "weeks_ahead": weeks_ahead,
        "predicted_state": {"skin_score": 80, "acne_level": 1, "pigmentation_level": 1},
    })
    twin.future_simulations = simulations
    await db.commit()
    return APIResponse(success=True, message="Simulation created")


@router.get("/{customer_id}/simulations", response_model=APIResponse)
async def get_simulations(customer_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(
        select(DigitalBeautyTwin).where(DigitalBeautyTwin.customer_id == str(customer_id))
    )
    twin = result.scalar_one_or_none()
    if not twin:
        raise HTTPException(404, "Digital twin not found")
    return APIResponse(success=True, data=twin.future_simulations or [])
