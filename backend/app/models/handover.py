"""Client Handover & Relationship Memory models."""
from sqlalchemy import String, Boolean, ForeignKey, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, TimestampMixin, generate_uuid


class ClientHandover(Base, TimestampMixin):
    __tablename__ = "client_handovers"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customer_profiles.id"), nullable=False)
    from_stylist_id: Mapped[str] = mapped_column(String(36), ForeignKey("staff_profiles.id"), nullable=False)
    to_stylist_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("staff_profiles.id"))
    reason: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str | None] = mapped_column(String(20))
    customer_preferences: Mapped[dict | None] = mapped_column(JSON)
    conversation_style: Mapped[str | None] = mapped_column(String(100))
    relationship_notes: Mapped[str | None] = mapped_column(Text)
    service_history_summary: Mapped[dict | None] = mapped_column(JSON)
    handover_date: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    acknowledged_by_customer: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<ClientHandover {self.from_stylist_id}→{self.to_stylist_id}>"


class StylistCustomerMemory(Base, TimestampMixin):
    __tablename__ = "stylist_customer_memories"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    stylist_id: Mapped[str] = mapped_column(String(36), ForeignKey("staff_profiles.id"), nullable=False)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customer_profiles.id"), nullable=False)
    memory_type: Mapped[str | None] = mapped_column(String(50))
    content: Mapped[str | None] = mapped_column(Text)
    importance: Mapped[str | None] = mapped_column(String(20))
    source: Mapped[str | None] = mapped_column(String(20))
    session_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("service_sessions.id"))

    def __repr__(self) -> str:
        return f"<StylistCustomerMemory {self.memory_type}>"
