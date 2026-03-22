"""SmartQueueEntry model — real-time walk-in queue management."""
from sqlalchemy import String, Boolean, ForeignKey, Integer, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.database import Base, TimestampMixin, generate_uuid


class QueueStatus(str, enum.Enum):
    WAITING = "waiting"
    ASSIGNED = "assigned"
    IN_SERVICE = "in_service"
    COMPLETED = "completed"
    LEFT = "left"


class WalkInSource(str, enum.Enum):
    IN_PERSON = "in_person"
    WHATSAPP = "whatsapp"
    APP_CHECKIN = "app_checkin"


class SmartQueueEntry(Base, TimestampMixin):
    __tablename__ = "smart_queue_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    location_id: Mapped[str] = mapped_column(String(36), ForeignKey("locations.id"), nullable=False)
    customer_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("customer_profiles.id"))
    customer_name: Mapped[str | None] = mapped_column(String(200))
    customer_phone: Mapped[str | None] = mapped_column(String(20))

    service_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("services.id"))
    preferred_stylist_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("staff_profiles.id"))

    status: Mapped[QueueStatus] = mapped_column(String(50), default=QueueStatus.WAITING)
    position_in_queue: Mapped[int | None] = mapped_column(Integer)
    estimated_wait_mins: Mapped[int | None] = mapped_column(Integer)
    actual_wait_mins: Mapped[int | None] = mapped_column(Integer)

    joined_queue_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    assigned_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    service_started_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    service_completed_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))

    notified_by_whatsapp: Mapped[bool] = mapped_column(Boolean, default=False)
    notification_sent_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    notification_message: Mapped[str | None] = mapped_column(Text)

    walk_in_source: Mapped[WalkInSource | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text)

    # Waitlist support (PS-05.07)
    is_waitlist: Mapped[bool] = mapped_column(Boolean, default=False)
    promoted_from_waitlist: Mapped[bool] = mapped_column(Boolean, default=False)
    original_booking_id: Mapped[str | None] = mapped_column(String(36))

    def __repr__(self) -> str:
        status_str = self.status.value if hasattr(self.status, 'value') else str(self.status)
        return f"<SmartQueueEntry pos={self.position_in_queue} ({status_str})>"
