"""TrendSignal model — social listening, demand forecasting, proactive alerts."""
from sqlalchemy import String, Boolean, Text, Numeric, Date, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.database import Base, TimestampMixin, generate_uuid


class TrendTrajectory(str, enum.Enum):
    EMERGING = "emerging"
    GROWING = "growing"
    PEAK = "peak"
    DECLINING = "declining"


class TrendLongevity(str, enum.Enum):
    FAD = "fad"
    TREND = "trend"
    MOVEMENT = "movement"


class TrendSignal(Base, TimestampMixin):
    __tablename__ = "trend_signals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    trend_name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str | None] = mapped_column(String(255), unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    service_category: Mapped[str | None] = mapped_column(String(100))
    applicable_regions: Mapped[list | None] = mapped_column(JSON)
    applicable_cities: Mapped[list | None] = mapped_column(JSON)

    overall_signal_strength: Mapped[float | None] = mapped_column(Numeric(4, 2))
    social_media_score: Mapped[float | None] = mapped_column(Numeric(4, 2))
    search_trend_score: Mapped[float | None] = mapped_column(Numeric(4, 2))
    booking_demand_score: Mapped[float | None] = mapped_column(Numeric(4, 2))
    influencer_score: Mapped[float | None] = mapped_column(Numeric(4, 2))
    celebrity_trigger: Mapped[str | None] = mapped_column(Text)

    trajectory: Mapped[TrendTrajectory | None] = mapped_column(String(50))
    longevity_label: Mapped[TrendLongevity | None] = mapped_column(String(50))
    predicted_peak_date: Mapped[str | None] = mapped_column(Date)
    confidence_level: Mapped[float | None] = mapped_column(Numeric(3, 2))

    inventory_actions: Mapped[dict | None] = mapped_column(JSON)
    training_actions: Mapped[dict | None] = mapped_column(JSON)
    marketing_actions: Mapped[dict | None] = mapped_column(JSON)

    cover_image_url: Mapped[str | None] = mapped_column(Text)
    example_image_urls: Mapped[list | None] = mapped_column(JSON)
    source_urls: Mapped[list | None] = mapped_column(JSON)
    climate_correlation: Mapped[dict | None] = mapped_column(JSON)

    detected_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Seasonal patterns (PS-04.05)
    seasonal_pattern: Mapped[dict | None] = mapped_column(JSON)
    # Competitive context (PS-04.08)
    competitive_context: Mapped[dict | None] = mapped_column(JSON)

    def __repr__(self) -> str:
        return f"<TrendSignal {self.trend_name} ({self.trajectory})>"
