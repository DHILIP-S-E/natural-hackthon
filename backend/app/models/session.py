"""ServiceSession model — live session during service delivery. Offline-capable."""
from sqlalchemy import String, Boolean, ForeignKey, Integer, Text, Numeric, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base, TimestampMixin, generate_uuid


class SessionStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class ServiceSession(Base, TimestampMixin):
    __tablename__ = "service_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    booking_id: Mapped[str] = mapped_column(String(36), ForeignKey("bookings.id"), unique=True)
    sop_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("sops.id"))
    sop_version: Mapped[str | None] = mapped_column(String(20))
    soulskin_session_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("soulskin_sessions.id"))

    status: Mapped[SessionStatus] = mapped_column(String(50), default=SessionStatus.NOT_STARTED)
    steps_total: Mapped[int | None] = mapped_column(Integer)
    steps_completed: Mapped[list | None] = mapped_column(JSON)
    current_step: Mapped[int] = mapped_column(Integer, default=1)
    started_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    paused_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    resumed_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))

    products_used: Mapped[dict | None] = mapped_column(JSON)
    chemical_ratios_used: Mapped[dict | None] = mapped_column(JSON)
    processing_start_time: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    processing_end_time: Mapped[str | None] = mapped_column(DateTime(timezone=True))

    deviations: Mapped[dict | None] = mapped_column(JSON)
    ai_coaching_prompts: Mapped[dict | None] = mapped_column(JSON)
    soulskin_active: Mapped[bool] = mapped_column(Boolean, default=False)
    archetype_applied: Mapped[str | None] = mapped_column(String(20))

    before_image_url: Mapped[str | None] = mapped_column(Text)
    after_image_url: Mapped[str | None] = mapped_column(Text)

    quality_score: Mapped[float | None] = mapped_column(Numeric(4, 2))
    sop_compliance_pct: Mapped[float | None] = mapped_column(Numeric(4, 2))
    timing_compliance: Mapped[float | None] = mapped_column(Numeric(4, 2))

    stylist_notes: Mapped[str | None] = mapped_column(Text)

    # Offline sync fields
    last_synced_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    has_offline_changes: Mapped[bool] = mapped_column(Boolean, default=False)
    offline_actions_queue: Mapped[dict | None] = mapped_column(JSON)

    # Pre-service consultation (PS-01.01)
    consultation_checklist: Mapped[dict | None] = mapped_column(JSON)
    consultation_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    consultation_completed_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))

    # Chemical safety verification (PS-01.08)
    chemical_safety_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    chemical_safety_photo_url: Mapped[str | None] = mapped_column(Text)
    chemical_safety_signature_url: Mapped[str | None] = mapped_column(Text)
    chemical_safety_verified_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    chemical_safety_verified_by: Mapped[str | None] = mapped_column(String(36))

    # In-service micro-feedback (PS-05.05)
    in_service_feedback: Mapped[dict | None] = mapped_column(JSON)
    comfort_level: Mapped[int | None] = mapped_column(Integer)

    # Relationships
    booking = relationship("Booking", foreign_keys=[booking_id])
    sop = relationship("SOP", foreign_keys=[sop_id])

    def __repr__(self) -> str:
        status_str = self.status.value if hasattr(self.status, 'value') else str(self.status)
        return f"<ServiceSession booking={self.booking_id} ({status_str})>"
