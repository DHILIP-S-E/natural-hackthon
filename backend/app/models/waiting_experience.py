"""Waiting Experience & Ambient Control models."""
from sqlalchemy import String, Boolean, ForeignKey, Text, Numeric, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, TimestampMixin, generate_uuid


class WaitingExperience(Base, TimestampMixin):
    __tablename__ = "waiting_experiences"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    queue_entry_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("smart_queue_entries.id"))
    booking_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("bookings.id"))
    customer_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("customer_profiles.id"))
    location_id: Mapped[str] = mapped_column(String(36), ForeignKey("locations.id"), nullable=False)
    experience_type: Mapped[str | None] = mapped_column(String(50))
    content_served: Mapped[dict | None] = mapped_column(JSON)
    started_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    engagement_score: Mapped[float | None] = mapped_column(Numeric(4, 2))
    led_to_addon: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<WaitingExperience {self.experience_type}>"


class AmbientControl(Base, TimestampMixin):
    __tablename__ = "ambient_controls"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    location_id: Mapped[str] = mapped_column(String(36), ForeignKey("locations.id"), nullable=False)
    zone: Mapped[str | None] = mapped_column(String(50))
    lighting_preset: Mapped[str | None] = mapped_column(String(50))
    music_playlist: Mapped[str | None] = mapped_column(String(255))
    aroma_preset: Mapped[str | None] = mapped_column(String(50))
    temperature_target: Mapped[float | None] = mapped_column(Numeric(4, 1))
    active_archetype: Mapped[str | None] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    scheduled_presets: Mapped[dict | None] = mapped_column(JSON)

    def __repr__(self) -> str:
        return f"<AmbientControl {self.zone} ({self.lighting_preset})>"
