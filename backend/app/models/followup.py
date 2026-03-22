"""Post-Service Follow-Up models."""
from sqlalchemy import String, Boolean, ForeignKey, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, TimestampMixin, generate_uuid


class FollowUpSequence(Base, TimestampMixin):
    __tablename__ = "followup_sequences"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    booking_id: Mapped[str] = mapped_column(String(36), ForeignKey("bookings.id"), nullable=False)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customer_profiles.id"), nullable=False)
    location_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("locations.id"))
    sequence_type: Mapped[str | None] = mapped_column(String(30))
    status: Mapped[str | None] = mapped_column(String(20))
    steps: Mapped[dict | None] = mapped_column(JSON)
    started_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    customer_responded: Mapped[bool] = mapped_column(Boolean, default=False)
    response_sentiment: Mapped[str | None] = mapped_column(String(20))
    rebooking_triggered: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<FollowUpSequence {self.sequence_type} ({self.status})>"
