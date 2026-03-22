"""Booking model — appointment and walk-in bookings."""
from sqlalchemy import String, Boolean, ForeignKey, Integer, Text, Numeric, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base, TimestampMixin, generate_uuid


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    PARTIAL = "partial"
    REFUNDED = "refunded"


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    CARD = "card"
    UPI = "upi"
    WALLET = "wallet"


class BookingSource(str, enum.Enum):
    WALK_IN = "walk_in"
    APP = "app"
    WHATSAPP = "whatsapp"
    PHONE = "phone"
    WEBSITE = "website"
    QUEUE = "queue"


class Booking(Base, TimestampMixin):
    __tablename__ = "bookings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    booking_number: Mapped[str | None] = mapped_column(String(20), unique=True)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customer_profiles.id"), nullable=False)
    location_id: Mapped[str] = mapped_column(String(36), ForeignKey("locations.id"), nullable=False)
    stylist_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("staff_profiles.id"))
    service_id: Mapped[str] = mapped_column(String(36), ForeignKey("services.id"), nullable=False)
    soulskin_session_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("soulskin_sessions.id"))
    ar_session_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("ar_mirror_sessions.id"))
    queue_entry_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("smart_queue_entries.id"))

    status: Mapped[BookingStatus] = mapped_column(String(50), default=BookingStatus.PENDING)
    scheduled_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
    actual_start_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    actual_end_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    duration_variance_minutes: Mapped[int | None] = mapped_column(Integer)

    base_price: Mapped[float | None] = mapped_column(Numeric(10, 2))
    discount_percent: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    discount_reason: Mapped[str | None] = mapped_column(String(255))
    final_price: Mapped[float | None] = mapped_column(Numeric(10, 2))
    payment_status: Mapped[PaymentStatus | None] = mapped_column(String(50))
    payment_method: Mapped[PaymentMethod | None] = mapped_column(String(50))

    source: Mapped[BookingSource | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text)
    internal_notes: Mapped[str | None] = mapped_column(Text)
    add_on_services: Mapped[list | None] = mapped_column(JSON)

    cancellation_reason: Mapped[str | None] = mapped_column(Text)
    cancelled_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    cancelled_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    rescheduled_from: Mapped[str | None] = mapped_column(String(36), ForeignKey("bookings.id"))

    reminder_sent_24h: Mapped[bool] = mapped_column(Boolean, default=False)
    reminder_sent_2h: Mapped[bool] = mapped_column(Boolean, default=False)
    followup_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    journey_plan_generated: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    customer = relationship("CustomerProfile", foreign_keys=[customer_id])
    location = relationship("Location", foreign_keys=[location_id])
    stylist = relationship("StaffProfile", foreign_keys=[stylist_id])
    service = relationship("Service", foreign_keys=[service_id])

    def __repr__(self) -> str:
        status_str = self.status.value if hasattr(self.status, 'value') else str(self.status)
        return f"<Booking {self.booking_number} ({status_str})>"
