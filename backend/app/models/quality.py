"""Quality & Skill Assessment models."""
from sqlalchemy import String, Boolean, ForeignKey, Integer, Text, Numeric, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.staff import SkillLevel
import enum

from app.database import Base, TimestampMixin, generate_uuid


class AssessmentType(str, enum.Enum):
    SELF = "self"
    MANAGER = "manager"
    AI = "ai"
    PEER = "peer"
    EXTERNAL_TRAINER = "external_trainer"


class QualityAssessment(Base, TimestampMixin):
    __tablename__ = "quality_assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    booking_id: Mapped[str] = mapped_column(String(36), ForeignKey("bookings.id"), unique=True)
    session_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("service_sessions.id"))
    stylist_id: Mapped[str] = mapped_column(String(36), ForeignKey("staff_profiles.id"), nullable=False)
    location_id: Mapped[str] = mapped_column(String(36), ForeignKey("locations.id"), nullable=False)
    service_id: Mapped[str] = mapped_column(String(36), ForeignKey("services.id"), nullable=False)

    sop_compliance_score: Mapped[float | None] = mapped_column(Numeric(4, 2))
    timing_score: Mapped[float | None] = mapped_column(Numeric(4, 2))
    customer_rating: Mapped[int | None] = mapped_column(Integer)
    manager_rating: Mapped[int | None] = mapped_column(Integer)
    overall_score: Mapped[float | None] = mapped_column(Numeric(4, 2))

    before_image_url: Mapped[str | None] = mapped_column(Text)
    after_image_url: Mapped[str | None] = mapped_column(Text)
    ai_analysis_result: Mapped[dict | None] = mapped_column(JSON)

    ai_feedback: Mapped[str | None] = mapped_column(Text)
    ai_feedback_generated_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))

    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False)
    flag_reason: Mapped[str | None] = mapped_column(Text)
    reviewed_by_manager: Mapped[bool] = mapped_column(Boolean, default=False)
    manager_review_note: Mapped[str | None] = mapped_column(Text)

    soulskin_alignment_score: Mapped[float | None] = mapped_column(Numeric(4, 2))

    def __repr__(self) -> str:
        return f"<QualityAssessment score={self.overall_score}>"


class SkillAssessment(Base, TimestampMixin):
    __tablename__ = "skill_assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    staff_id: Mapped[str] = mapped_column(String(36), ForeignKey("staff_profiles.id"), nullable=False)
    assessed_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    assessment_type: Mapped[AssessmentType | None] = mapped_column(String(50))
    service_category: Mapped[str | None] = mapped_column(String(100))
    skill_area: Mapped[str | None] = mapped_column(String(100))
    current_level: Mapped[SkillLevel | None] = mapped_column(String(50))
    score: Mapped[float | None] = mapped_column(Numeric(4, 2))
    rubric_scores: Mapped[dict | None] = mapped_column(JSON)
    l2_gap_items: Mapped[list | None] = mapped_column(JSON)
    l3_gap_items: Mapped[list | None] = mapped_column(JSON)
    recommended_training: Mapped[list | None] = mapped_column(JSON)
    soulskin_certified: Mapped[bool | None] = mapped_column(Boolean)
    assessment_notes: Mapped[str | None] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<SkillAssessment staff={self.staff_id} score={self.score}>"
