"""Campaign, Competitive Intel, and Celebrity Trend Source models."""
from sqlalchemy import String, Boolean, ForeignKey, Integer, Text, Numeric, Date, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, TimestampMixin, generate_uuid


class Campaign(Base, TimestampMixin):
    __tablename__ = "campaigns"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    campaign_type: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str | None] = mapped_column(String(20))
    target_locations: Mapped[list | None] = mapped_column(JSON)
    target_customer_segments: Mapped[dict | None] = mapped_column(JSON)
    linked_trend_ids: Mapped[list | None] = mapped_column(JSON)
    linked_services: Mapped[list | None] = mapped_column(JSON)
    start_date: Mapped[str | None] = mapped_column(Date)
    end_date: Mapped[str | None] = mapped_column(Date)
    budget: Mapped[float | None] = mapped_column(Numeric(12, 2))
    channels: Mapped[list | None] = mapped_column(JSON)
    content_template: Mapped[dict | None] = mapped_column(JSON)
    expected_revenue_uplift: Mapped[float | None] = mapped_column(Numeric(12, 2))
    actual_revenue_generated: Mapped[float | None] = mapped_column(Numeric(12, 2))
    bookings_generated: Mapped[int | None] = mapped_column(Integer)
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))

    def __repr__(self) -> str:
        return f"<Campaign {self.title} ({self.status})>"


class CompetitiveIntel(Base, TimestampMixin):
    __tablename__ = "competitive_intel"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    competitor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    intel_type: Mapped[str | None] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(Text)
    city: Mapped[str | None] = mapped_column(String(100))
    relevance_score: Mapped[float | None] = mapped_column(Numeric(3, 2))
    action_recommended: Mapped[str | None] = mapped_column(Text)
    is_actioned: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<CompetitiveIntel {self.competitor_name} ({self.intel_type})>"


class CelebrityTrendSource(Base, TimestampMixin):
    __tablename__ = "celebrity_trend_sources"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    celebrity_name: Mapped[str] = mapped_column(String(255), nullable=False)
    media_source: Mapped[str | None] = mapped_column(String(50))
    look_description: Mapped[str | None] = mapped_column(Text)
    image_urls: Mapped[list | None] = mapped_column(JSON)
    detected_services: Mapped[list | None] = mapped_column(JSON)
    virality_score: Mapped[float | None] = mapped_column(Numeric(4, 2))
    linked_trend_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("trend_signals.id"))
    detected_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))

    def __repr__(self) -> str:
        return f"<CelebrityTrendSource {self.celebrity_name}>"
