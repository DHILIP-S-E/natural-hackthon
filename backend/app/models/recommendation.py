"""Service Recommendation models — upsell/cross-sell engine."""
from sqlalchemy import String, Boolean, ForeignKey, Text, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, TimestampMixin, generate_uuid


class ServiceRecommendation(Base, TimestampMixin):
    __tablename__ = "service_recommendations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    booking_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("bookings.id"))
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customer_profiles.id"), nullable=False)
    stylist_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("staff_profiles.id"))
    location_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("locations.id"))
    recommendation_type: Mapped[str | None] = mapped_column(String(30))
    trigger_context: Mapped[str | None] = mapped_column(String(30))
    recommended_service_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("services.id"))
    reason: Mapped[str | None] = mapped_column(Text)
    confidence_score: Mapped[float | None] = mapped_column(Numeric(3, 2))
    presented_to_customer: Mapped[bool] = mapped_column(Boolean, default=False)
    accepted: Mapped[bool | None] = mapped_column(Boolean)
    accepted_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    revenue_generated: Mapped[float | None] = mapped_column(Numeric(10, 2))

    def __repr__(self) -> str:
        return f"<ServiceRecommendation {self.recommendation_type}>"
