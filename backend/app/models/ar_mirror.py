"""AR Mirror Session model — Smart Mirror try-on sessions."""
from sqlalchemy import String, Boolean, ForeignKey, Integer, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.database import Base, TimestampMixin, generate_uuid


class MirrorSessionType(str, enum.Enum):
    HAIRSTYLE = "hairstyle"
    HAIR_COLOR = "hair_color"
    MAKEUP = "makeup"
    SKINCARE_PREVIEW = "skincare_preview"
    FULL_LOOK = "full_look"


class MirrorInitiator(str, enum.Enum):
    CUSTOMER = "customer"
    STYLIST = "stylist"


class ARMirrorSession(Base, TimestampMixin):
    __tablename__ = "ar_mirror_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customer_profiles.id"), nullable=False)
    booking_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("bookings.id", use_alter=True))
    location_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("locations.id"))
    initiated_by: Mapped[MirrorInitiator | None] = mapped_column(String(50))

    session_type: Mapped[MirrorSessionType | None] = mapped_column(String(50))
    tryons: Mapped[dict | None] = mapped_column(JSON)
    final_selection: Mapped[dict | None] = mapped_column(JSON)
    climate_recommendations: Mapped[dict | None] = mapped_column(JSON)

    session_duration_secs: Mapped[int | None] = mapped_column(Integer)
    saved_images: Mapped[list | None] = mapped_column(JSON)
    booking_created_after: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<ARMirrorSession {self.session_type}>"
