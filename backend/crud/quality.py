"""CRUD — Quality assessments domain."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from models.quality import QualityAssessment


async def get_by_id(db: AsyncSession, qa_id: str) -> QualityAssessment | None:
    result = await db.execute(select(QualityAssessment).where(QualityAssessment.id == qa_id))
    return result.scalar_one_or_none()


async def get_by_stylist(db: AsyncSession, staff_id: str, limit: int = 50) -> list[QualityAssessment]:
    result = await db.execute(
        select(QualityAssessment)
        .where(QualityAssessment.stylist_id == staff_id)
        .order_by(QualityAssessment.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_by_location(db: AsyncSession, location_id: str, limit: int = 100) -> list[QualityAssessment]:
    result = await db.execute(
        select(QualityAssessment)
        .where(QualityAssessment.location_id == location_id)
        .order_by(QualityAssessment.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def create(db: AsyncSession, data: dict) -> QualityAssessment:
    qa = QualityAssessment(**data)
    db.add(qa)
    await db.flush()
    return qa


async def update(db: AsyncSession, qa: QualityAssessment, data: dict) -> QualityAssessment:
    for k, v in data.items():
        setattr(qa, k, v)
    await db.flush()
    return qa
