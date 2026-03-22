"""Training router — Staff training records and ROI tracking."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db, enum_val
from app.dependencies import get_current_user, require_role
from app.models import TrainingRecord, TrainingType
from app.schemas.common import APIResponse

router = APIRouter(prefix="/training", tags=["Training"])


@router.get("/", response_model=APIResponse)
async def list_training(staff_id: UUID = None, page: int = 1, per_page: int = 20,
                        db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    q = select(TrainingRecord).order_by(TrainingRecord.created_at.desc())
    if staff_id:
        q = q.where(TrainingRecord.staff_id == str(staff_id))
    q = q.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(q)
    records = result.scalars().all()
    return APIResponse(success=True, data=[{
        "id": str(r.id), "staff_id": r.staff_id,
        "training_name": r.training_name,
        "training_type": enum_val(r.training_type) if r.training_type else None,
        "service_category": r.service_category,
        "provider": r.provider, "trainer_name": r.trainer_name,
        "start_date": str(r.start_date) if r.start_date else None,
        "end_date": str(r.end_date) if r.end_date else None,
        "hours_completed": float(r.hours_completed) if r.hours_completed else None,
        "cost_to_company": float(r.cost_to_company) if r.cost_to_company else None,
        "passed": r.passed, "score": float(r.score) if r.score else None,
        "certificate_url": r.certificate_url,
        "includes_soulskin": r.includes_soulskin,
        "revenue_before": float(r.revenue_before) if r.revenue_before else None,
        "revenue_after": float(r.revenue_after) if r.revenue_after else None,
        "quality_score_before": float(r.quality_score_before) if r.quality_score_before else None,
        "quality_score_after": float(r.quality_score_after) if r.quality_score_after else None,
    } for r in records])


@router.post("/", response_model=APIResponse)
async def create_training(
    staff_id: UUID, training_name: str, training_type: str = "online",
    service_category: str = None, provider: str = None, trainer_name: str = None,
    hours_completed: float = 0, cost_to_company: float = 0,
    passed: bool = False, score: float = None,
    includes_soulskin: bool = False,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(["salon_manager", "franchise_owner", "super_admin"])),
):
    record = TrainingRecord(
        staff_id=str(staff_id), training_name=training_name,
        training_type=TrainingType(training_type),
        service_category=service_category,
        provider=provider, trainer_name=trainer_name,
        hours_completed=hours_completed, cost_to_company=cost_to_company,
        passed=passed, score=score,
        includes_soulskin=includes_soulskin,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return APIResponse(success=True, data={"id": str(record.id)}, message="Training record created")


@router.get("/{record_id}", response_model=APIResponse)
async def get_training(record_id: UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    record = await db.get(TrainingRecord, str(record_id))
    if not record:
        raise HTTPException(404, "Training record not found")
    return APIResponse(success=True, data={
        "id": str(record.id), "staff_id": record.staff_id,
        "training_name": record.training_name,
        "training_type": enum_val(record.training_type) if record.training_type else None,
        "service_category": record.service_category,
        "provider": record.provider, "trainer_name": record.trainer_name,
        "start_date": str(record.start_date) if record.start_date else None,
        "end_date": str(record.end_date) if record.end_date else None,
        "hours_completed": float(record.hours_completed) if record.hours_completed else None,
        "cost_to_company": float(record.cost_to_company) if record.cost_to_company else None,
        "passed": record.passed, "score": float(record.score) if record.score else None,
        "certificate_url": record.certificate_url,
        "includes_soulskin": record.includes_soulskin,
        "revenue_before": float(record.revenue_before) if record.revenue_before else None,
        "revenue_after": float(record.revenue_after) if record.revenue_after else None,
        "quality_score_before": float(record.quality_score_before) if record.quality_score_before else None,
        "quality_score_after": float(record.quality_score_after) if record.quality_score_after else None,
        "notes": record.notes,
    })


@router.get("/stats/roi", response_model=APIResponse)
async def training_roi(location_id: UUID = None, db: AsyncSession = Depends(get_db),
                       user=Depends(require_role(["salon_manager", "franchise_owner", "regional_manager", "super_admin"]))):
    q = select(
        func.count(TrainingRecord.id).label("total_trainings"),
        func.sum(TrainingRecord.cost_to_company).label("total_cost"),
        func.sum(TrainingRecord.hours_completed).label("total_hours"),
        func.avg(TrainingRecord.score).label("avg_score"),
    )
    result = await db.execute(q)
    row = result.one()
    return APIResponse(success=True, data={
        "total_trainings": row.total_trainings,
        "total_cost": float(row.total_cost or 0),
        "total_hours": float(row.total_hours or 0),
        "avg_score": round(float(row.avg_score or 0), 2),
    })
