"""StaffProfile model — extended profile for stylist, manager, franchise_owner users."""
from sqlalchemy import String, Boolean, ForeignKey, Integer, Date, Text, Numeric, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base, TimestampMixin, generate_uuid


class SkillLevel(str, enum.Enum):
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"


class AttritionRisk(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class StaffProfile(Base, TimestampMixin):
    __tablename__ = "staff_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    location_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("locations.id"))
    employee_id: Mapped[str | None] = mapped_column(String(50), unique=True)
    designation: Mapped[str | None] = mapped_column(String(100))
    specializations: Mapped[list | None] = mapped_column(JSON)
    skill_level: Mapped[SkillLevel | None] = mapped_column(String(50))
    years_experience: Mapped[float | None] = mapped_column(Numeric(4, 1))
    joining_date: Mapped[str | None] = mapped_column(Date)
    bio: Mapped[str | None] = mapped_column(Text)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    weekly_off_day: Mapped[str | None] = mapped_column(String(10))
    attrition_risk_score: Mapped[float | None] = mapped_column(Numeric(3, 2))
    attrition_risk_label: Mapped[AttritionRisk | None] = mapped_column(String(50))
    current_rating: Mapped[float | None] = mapped_column(Numeric(3, 2))
    total_services_done: Mapped[int] = mapped_column(Integer, default=0)
    total_revenue_generated: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    soulskin_certified: Mapped[bool] = mapped_column(Boolean, default=False)
    languages_spoken: Mapped[list | None] = mapped_column(JSON)
    portfolio_image_urls: Mapped[list | None] = mapped_column(JSON)
    instagram_handle: Mapped[str | None] = mapped_column(String(100))

    # Relationships
    user = relationship("User", back_populates="staff_profile")
    location = relationship("Location", back_populates="staff")

    def __repr__(self) -> str:
        return f"<StaffProfile {self.employee_id}>"
