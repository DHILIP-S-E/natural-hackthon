"""DigitalBeautyTwin model — 3D digital face model, skin timeline, future simulations."""
from sqlalchemy import String, Boolean, ForeignKey, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, TimestampMixin, generate_uuid


class DigitalBeautyTwin(Base, TimestampMixin):
    __tablename__ = "digital_beauty_twins"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customer_profiles.id"), unique=True)

    model_data_url: Mapped[str | None] = mapped_column(Text)
    texture_url: Mapped[str | None] = mapped_column(Text)
    last_rebuilt_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))

    skin_timeline: Mapped[dict | None] = mapped_column(JSON)
    future_simulations: Mapped[dict | None] = mapped_column(JSON)
    hairstyle_tryons: Mapped[dict | None] = mapped_column(JSON)

    consent_given: Mapped[bool] = mapped_column(Boolean, default=False)
    consent_date: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<DigitalBeautyTwin customer={self.customer_id}>"
