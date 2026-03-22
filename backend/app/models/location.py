"""Location model — each Naturals salon outlet."""
from sqlalchemy import String, Boolean, DateTime, Text, Integer, ForeignKey, Date, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Numeric

from app.database import Base, TimestampMixin, SoftDeleteMixin, generate_uuid


class Location(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "locations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str | None] = mapped_column(String(20), unique=True)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    pincode: Mapped[str | None] = mapped_column(String(10))
    region: Mapped[str | None] = mapped_column(String(100))
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 8))
    longitude: Mapped[float | None] = mapped_column(Numeric(11, 8))
    phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255))
    franchise_owner_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    manager_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    opening_date: Mapped[str | None] = mapped_column(Date)
    monthly_revenue_target: Mapped[float | None] = mapped_column(Numeric(12, 2))
    seating_capacity: Mapped[int | None] = mapped_column(Integer)
    operating_hours: Mapped[dict | None] = mapped_column(JSON)
    smart_mirror_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    soulskin_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    climate_zone: Mapped[str | None] = mapped_column(String(50))

    # Relationships
    franchise_owner = relationship("User", foreign_keys=[franchise_owner_id])
    manager = relationship("User", foreign_keys=[manager_id])
    staff = relationship("StaffProfile", back_populates="location")

    def __repr__(self) -> str:
        return f"<Location {self.code} - {self.name}>"
