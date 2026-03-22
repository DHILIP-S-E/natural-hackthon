"""Notification model — multi-channel notifications."""
from sqlalchemy import String, Boolean, ForeignKey, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.database import Base, TimestampMixin, generate_uuid


class NotificationChannel(str, enum.Enum):
    PUSH = "push"
    WHATSAPP = "whatsapp"
    SMS = "sms"
    EMAIL = "email"
    IN_APP = "in_app"


class NotificationPriority(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    notification_type: Mapped[str | None] = mapped_column(String(100))
    title: Mapped[str | None] = mapped_column(String(255))
    body: Mapped[str | None] = mapped_column(Text)
    data: Mapped[dict | None] = mapped_column(JSON)
    channel: Mapped[NotificationChannel | None] = mapped_column(String(50))
    priority: Mapped[NotificationPriority | None] = mapped_column(String(50))
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    read_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    failed_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    failure_reason: Mapped[str | None] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<Notification {self.notification_type} → {self.channel}>"
