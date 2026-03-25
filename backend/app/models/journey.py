"""BeautyJourneyPlan model — AI-generated 3/6 month roadmap."""
from sqlalchemy import String, Boolean, ForeignKey, Integer, Text, Numeric, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, TimestampMixin, generate_uuid


class BeautyJourneyPlan(Base, TimestampMixin):
    __tablename__ = "beauty_journey_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customer_profiles.id"), nullable=False)
    generated_after_booking_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("bookings.id"))
    plan_duration_weeks: Mapped[int | None] = mapped_column(Integer)
    primary_goal: Mapped[str | None] = mapped_column(Text)
    generated_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))

    milestones: Mapped[dict | None] = mapped_column(JSON)
    expected_outcomes: Mapped[dict | None] = mapped_column(JSON)
    skin_projection: Mapped[dict | None] = mapped_column(JSON)
    recommended_products: Mapped[list | None] = mapped_column(JSON)
    estimated_total_cost: Mapped[float | None] = mapped_column(Numeric(10, 2))

    ai_notes: Mapped[str | None] = mapped_column(Text)
    whatsapp_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    pdf_url: Mapped[str | None] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<BeautyJourneyPlan {self.plan_duration_weeks}wks goal={self.primary_goal}>"
