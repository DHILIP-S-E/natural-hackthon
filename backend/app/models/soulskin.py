"""SOULSKIN Session model — emotion-to-beauty intelligence."""
from sqlalchemy import String, Boolean, ForeignKey, Integer, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, TimestampMixin, generate_uuid


class SoulskinSession(Base, TimestampMixin):
    __tablename__ = "soulskin_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    booking_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("bookings.id", use_alter=True))
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customer_profiles.id"), nullable=False)
    stylist_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("staff_profiles.id"))
    location_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("locations.id"))

    # ══ THE 3 QUESTIONS ══
    question_1_song: Mapped[str | None] = mapped_column(Text)
    question_2_colour: Mapped[str | None] = mapped_column(String(100))
    question_3_word: Mapped[str | None] = mapped_column(String(100))

    # ══ AI-GENERATED SOUL READING ══
    soul_reading: Mapped[str | None] = mapped_column(Text)
    archetype: Mapped[str | None] = mapped_column(String(20))
    archetype_reason: Mapped[str | None] = mapped_column(Text)

    # ══ COMPLETE EXPERIENCE DESIGN (LLM-generated JSONB) ══
    service_protocol: Mapped[dict | None] = mapped_column(JSON)
    colour_direction: Mapped[dict | None] = mapped_column(JSON)
    sensory_environment: Mapped[dict | None] = mapped_column(JSON)
    touch_protocol: Mapped[dict | None] = mapped_column(JSON)
    custom_formula: Mapped[dict | None] = mapped_column(JSON)
    stylist_script: Mapped[dict | None] = mapped_column(JSON)
    mirror_monologue: Mapped[str | None] = mapped_column(Text)

    # ══ SOUL JOURNAL ENTRY ══
    journal_date: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    archetype_of_day: Mapped[str | None] = mapped_column(String(20))
    private_life_note: Mapped[str | None] = mapped_column(Text)
    look_created: Mapped[str | None] = mapped_column(Text)

    # ══ METADATA ══
    session_duration_mins: Mapped[int | None] = mapped_column(Integer)
    customer_reaction: Mapped[str | None] = mapped_column(String(50))
    session_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<SoulskinSession archetype={self.archetype}>"
