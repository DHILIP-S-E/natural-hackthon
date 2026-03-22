"""ClimateRecommendation model — real-time weather-based beauty advice per city."""
from sqlalchemy import String, Boolean, Integer, Text, Numeric, DateTime, Date, UniqueConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, TimestampMixin, generate_uuid


class ClimateRecommendation(Base, TimestampMixin):
    __tablename__ = "climate_recommendations"
    __table_args__ = (UniqueConstraint("city", "date_for", name="uq_climate_city_date"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    date_for: Mapped[str] = mapped_column(Date, nullable=False)
    fetched_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))

    temperature_celsius: Mapped[float | None] = mapped_column(Numeric(4, 1))
    humidity_pct: Mapped[float | None] = mapped_column(Numeric(4, 1))
    uv_index: Mapped[float | None] = mapped_column(Numeric(4, 2))
    aqi: Mapped[float | None] = mapped_column(Numeric(6, 2))
    weather_condition: Mapped[str | None] = mapped_column(String(100))

    hair_recommendations: Mapped[dict | None] = mapped_column(JSON)
    skin_recommendations: Mapped[dict | None] = mapped_column(JSON)
    general_advisory: Mapped[str | None] = mapped_column(Text)
    is_alert: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<ClimateRecommendation {self.city} {self.date_for}>"
