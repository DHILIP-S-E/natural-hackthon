"""MoodDetection model — CV-based mood analysis at check-in."""
from sqlalchemy import String, Boolean, ForeignKey, Numeric, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, TimestampMixin, generate_uuid


class MoodDetection(Base, TimestampMixin):
    __tablename__ = "mood_detections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customer_profiles.id"), nullable=False)
    booking_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("bookings.id"))
    captured_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))

    detected_emotion: Mapped[str | None] = mapped_column(String(50))
    emotion_confidence: Mapped[float | None] = mapped_column(Numeric(4, 2))
    secondary_emotion: Mapped[str | None] = mapped_column(String(50))
    energy_level: Mapped[str | None] = mapped_column(String(20))
    stress_indicators: Mapped[dict | None] = mapped_column(JSON)

    recommended_archetype: Mapped[str | None] = mapped_column(String(20))
    service_adjustment: Mapped[str | None] = mapped_column(Text)
    do_not_recommend: Mapped[list | None] = mapped_column(JSON)

    image_processed: Mapped[bool] = mapped_column(Boolean, default=True)
    image_stored: Mapped[bool] = mapped_column(Boolean, default=False)
    consent_given: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<MoodDetection {self.detected_emotion} ({self.emotion_confidence})>"
