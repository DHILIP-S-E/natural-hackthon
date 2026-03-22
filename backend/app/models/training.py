"""TrainingRecord model — staff training with ROI tracking."""
from sqlalchemy import String, Boolean, ForeignKey, Text, Numeric, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.database import Base, TimestampMixin, generate_uuid


class TrainingType(str, enum.Enum):
    CLASSROOM = "classroom"
    ONLINE = "online"
    ON_JOB = "on_job"
    EXTERNAL_WORKSHOP = "external_workshop"


class TrainingRecord(Base, TimestampMixin):
    __tablename__ = "training_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    staff_id: Mapped[str] = mapped_column(String(36), ForeignKey("staff_profiles.id"), nullable=False)
    training_name: Mapped[str | None] = mapped_column(String(255))
    training_type: Mapped[TrainingType | None] = mapped_column(String(50))
    service_category: Mapped[str | None] = mapped_column(String(100))
    provider: Mapped[str | None] = mapped_column(String(255))
    trainer_name: Mapped[str | None] = mapped_column(String(255))
    start_date: Mapped[str | None] = mapped_column(Date)
    end_date: Mapped[str | None] = mapped_column(Date)
    hours_completed: Mapped[float | None] = mapped_column(Numeric(5, 1))
    cost_to_company: Mapped[float | None] = mapped_column(Numeric(10, 2))
    passed: Mapped[bool | None] = mapped_column(Boolean)
    score: Mapped[float | None] = mapped_column(Numeric(4, 2))
    certificate_url: Mapped[str | None] = mapped_column(Text)
    includes_soulskin: Mapped[bool] = mapped_column(Boolean, default=False)

    # ROI tracking
    revenue_before: Mapped[float | None] = mapped_column(Numeric(12, 2))
    revenue_after: Mapped[float | None] = mapped_column(Numeric(12, 2))
    quality_score_before: Mapped[float | None] = mapped_column(Numeric(4, 2))
    quality_score_after: Mapped[float | None] = mapped_column(Numeric(4, 2))
    roi_calculated_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))

    notes: Mapped[str | None] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<TrainingRecord {self.training_name}>"
