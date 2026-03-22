"""CustomerFeedback model — ratings and sentiment analysis."""
from sqlalchemy import String, Boolean, ForeignKey, Integer, Text, Numeric, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.database import Base, TimestampMixin, generate_uuid


class Sentiment(str, enum.Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class FeedbackSource(str, enum.Enum):
    APP = "app"
    WHATSAPP = "whatsapp"
    GOOGLE = "google"
    SMS = "sms"
    IN_PERSON = "in_person"


class CustomerFeedback(Base, TimestampMixin):
    __tablename__ = "customer_feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    booking_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("bookings.id"))
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customer_profiles.id"), nullable=False)
    stylist_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("staff_profiles.id"))
    location_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("locations.id"))
    service_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("services.id"))
    soulskin_session_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("soulskin_sessions.id"))

    overall_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    service_rating: Mapped[int | None] = mapped_column(Integer)
    stylist_rating: Mapped[int | None] = mapped_column(Integer)
    ambiance_rating: Mapped[int | None] = mapped_column(Integer)
    value_for_money: Mapped[int | None] = mapped_column(Integer)
    soulskin_experience_rating: Mapped[int | None] = mapped_column(Integer)
    would_recommend: Mapped[bool | None] = mapped_column(Boolean)

    comment: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list | None] = mapped_column(JSON)
    sentiment: Mapped[Sentiment | None] = mapped_column(String(50))
    sentiment_score: Mapped[float | None] = mapped_column(Numeric(4, 2))

    source: Mapped[FeedbackSource | None] = mapped_column(String(50))
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_responded: Mapped[bool] = mapped_column(Boolean, default=False)
    response_text: Mapped[str | None] = mapped_column(Text)
    responded_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    responded_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))

    # Root cause mapping (PS-01.04)
    root_cause_sop_step: Mapped[int | None] = mapped_column(Integer)
    root_cause_category: Mapped[str | None] = mapped_column(String(100))
    root_cause_analysis: Mapped[dict | None] = mapped_column(JSON)
    linked_session_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("service_sessions.id"))

    def __repr__(self) -> str:
        return f"<CustomerFeedback rating={self.overall_rating} ({self.sentiment})>"
