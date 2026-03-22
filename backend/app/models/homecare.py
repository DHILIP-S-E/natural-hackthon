"""HomecarePlan model — personalized home care routines."""
from sqlalchemy import String, Boolean, ForeignKey, Integer, Text, DateTime, JSON, Date
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, TimestampMixin, generate_uuid


class HomecarePlan(Base, TimestampMixin):
    __tablename__ = "homecare_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customer_profiles.id"), nullable=False)
    booking_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("bookings.id"))
    soulskin_archetype: Mapped[str | None] = mapped_column(String(20))
    generated_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    plan_duration_weeks: Mapped[int | None] = mapped_column(Integer)

    hair_routine: Mapped[dict | None] = mapped_column(JSON)
    skin_routine: Mapped[dict | None] = mapped_column(JSON)
    climate_adjustments: Mapped[dict | None] = mapped_column(JSON)
    archetype_rituals: Mapped[dict | None] = mapped_column(JSON)
    product_recommendations: Mapped[dict | None] = mapped_column(JSON)

    dos: Mapped[list | None] = mapped_column(JSON)
    donts: Mapped[list | None] = mapped_column(JSON)
    next_visit_recommendation: Mapped[str | None] = mapped_column(String(255))
    next_visit_suggested_date: Mapped[str | None] = mapped_column(Date)
    ai_notes: Mapped[str | None] = mapped_column(Text)
    whatsapp_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    pdf_url: Mapped[str | None] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<HomecarePlan archetype={self.soulskin_archetype}>"
