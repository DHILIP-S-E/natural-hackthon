"""Staff Scheduling & Float System models."""
from sqlalchemy import String, Boolean, ForeignKey, Integer, Text, Date, Time, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, TimestampMixin, generate_uuid


class StaffSchedule(Base, TimestampMixin):
    __tablename__ = "staff_schedules"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    staff_id: Mapped[str] = mapped_column(String(36), ForeignKey("staff_profiles.id"), nullable=False)
    location_id: Mapped[str] = mapped_column(String(36), ForeignKey("locations.id"), nullable=False)
    date: Mapped[str] = mapped_column(Date, nullable=False)
    shift_start: Mapped[str | None] = mapped_column(Time)
    shift_end: Mapped[str | None] = mapped_column(Time)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    is_float: Mapped[bool] = mapped_column(Boolean, default=False)
    float_from_location_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("locations.id"))
    max_bookings: Mapped[int | None] = mapped_column(Integer)
    assigned_bookings: Mapped[int] = mapped_column(Integer, default=0)
    skills_for_day: Mapped[list | None] = mapped_column(JSON)

    def __repr__(self) -> str:
        return f"<StaffSchedule {self.staff_id} {self.date}>"


class FloatRequest(Base, TimestampMixin):
    __tablename__ = "float_requests"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    requesting_location_id: Mapped[str] = mapped_column(String(36), ForeignKey("locations.id"), nullable=False)
    providing_location_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("locations.id"))
    staff_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("staff_profiles.id"))
    date: Mapped[str] = mapped_column(Date, nullable=False)
    required_skill_level: Mapped[str | None] = mapped_column(String(10))
    required_service_categories: Mapped[list | None] = mapped_column(JSON)
    status: Mapped[str | None] = mapped_column(String(20))
    reason: Mapped[str | None] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<FloatRequest {self.requesting_location_id} ({self.status})>"
