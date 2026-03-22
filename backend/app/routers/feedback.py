"""Feedback router — Customer feedback with sentiment."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db, enum_val
from app.dependencies import get_current_user, require_role
from app.models import CustomerFeedback, Sentiment, FeedbackSource
from app.schemas.common import APIResponse

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.get("/", response_model=APIResponse)
async def list_feedback(location_id: UUID = None, stylist_id: UUID = None,
                        page: int = 1, per_page: int = 20,
                        db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    q = select(CustomerFeedback).order_by(CustomerFeedback.created_at.desc())
    if location_id:
        q = q.where(CustomerFeedback.location_id == location_id)
    if stylist_id:
        q = q.where(CustomerFeedback.stylist_id == stylist_id)
    q = q.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(q)
    entries = result.scalars().all()
    return APIResponse(success=True, data=[{
        "id": str(f.id), "overall_rating": f.overall_rating, "service_rating": f.service_rating,
        "stylist_rating": f.stylist_rating, "comment": f.comment,
        "sentiment": enum_val(f.sentiment) if f.sentiment else None,
        "sentiment_score": float(f.sentiment_score) if f.sentiment_score else None, "would_recommend": f.would_recommend,
        "soulskin_experience_rating": f.soulskin_experience_rating,
        "created_at": str(f.created_at) if f.created_at else None,
    } for f in entries])


@router.post("/", response_model=APIResponse)
async def create_feedback(
    customer_id: UUID, stylist_id: UUID, location_id: UUID, service_id: UUID,
    overall_rating: int, service_rating: int, stylist_rating: int,
    comment: str = None, would_recommend: bool = True,
    soulskin_experience_rating: int = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    feedback = CustomerFeedback(
        customer_id=customer_id, stylist_id=stylist_id, location_id=location_id,
        service_id=service_id, overall_rating=overall_rating, service_rating=service_rating,
        stylist_rating=stylist_rating, comment=comment, would_recommend=would_recommend,
        soulskin_experience_rating=soulskin_experience_rating,
        sentiment=Sentiment.POSITIVE if overall_rating >= 4 else Sentiment.NEUTRAL if overall_rating == 3 else Sentiment.NEGATIVE,
        sentiment_score=overall_rating / 5.0,
        source=FeedbackSource.APP, is_verified=True,
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)
    return APIResponse(success=True, data={"id": str(feedback.id)}, message="Feedback submitted")


@router.get("/stats", response_model=APIResponse)
async def feedback_stats(location_id: UUID = None, db: AsyncSession = Depends(get_db),
                         user=Depends(require_role(["salon_manager", "franchise_owner", "regional_manager", "super_admin"]))):
    from sqlalchemy import func, Integer
    q = select(
        func.avg(CustomerFeedback.overall_rating).label("avg_rating"),
        func.count(CustomerFeedback.id).label("total"),
        func.sum(CustomerFeedback.would_recommend.cast(Integer)).label("recommend_count"),
    )
    if location_id:
        q = q.where(CustomerFeedback.location_id == location_id)
    result = await db.execute(q)
    row = result.one()
    return APIResponse(success=True, data={
        "avg_rating": round(float(row.avg_rating or 0), 2),
        "total_feedback": row.total,
        "recommend_count": int(row.recommend_count or 0),
    })
