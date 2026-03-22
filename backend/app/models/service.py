"""Service & SOP models — master service catalog + step-by-step guides."""
from sqlalchemy import String, Boolean, ForeignKey, Integer, Text, Numeric, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.staff import SkillLevel

from app.database import Base, TimestampMixin, generate_uuid


class Service(Base, TimestampMixin):
    __tablename__ = "services"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100))
    subcategory: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    short_description: Mapped[str | None] = mapped_column(String(255))
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    base_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    min_price: Mapped[float | None] = mapped_column(Numeric(10, 2))
    max_price: Mapped[float | None] = mapped_column(Numeric(10, 2))
    skill_required: Mapped[SkillLevel | None] = mapped_column(String(50))
    is_chemical: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sop_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("sops.id"))
    image_url: Mapped[str | None] = mapped_column(Text)
    ar_preview_available: Mapped[bool] = mapped_column(Boolean, default=False)
    tags: Mapped[list | None] = mapped_column(JSON)

    # Relationships
    sop = relationship("SOP", back_populates="service", foreign_keys=[sop_id])

    def __repr__(self) -> str:
        return f"<Service {self.name}>"


class SOP(Base, TimestampMixin):
    __tablename__ = "sops"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    service_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("services.id"))
    version: Mapped[str] = mapped_column(String(20), default="1.0")
    title: Mapped[str | None] = mapped_column(String(255))
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)
    steps: Mapped[dict] = mapped_column(JSON, nullable=False)
    soulskin_overlays: Mapped[dict | None] = mapped_column(JSON)
    products_required: Mapped[list | None] = mapped_column(JSON)
    chemicals_involved: Mapped[bool] = mapped_column(Boolean, default=False)
    chemical_ratios: Mapped[dict | None] = mapped_column(JSON)
    total_duration_minutes: Mapped[int | None] = mapped_column(Integer)
    created_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))

    # Pre-service checklist template (PS-01.01)
    pre_service_checklist: Mapped[dict | None] = mapped_column(JSON)

    # Relationships
    service = relationship("Service", back_populates="sop", foreign_keys="[Service.sop_id]")

    def __repr__(self) -> str:
        return f"<SOP {self.title} v{self.version}>"
