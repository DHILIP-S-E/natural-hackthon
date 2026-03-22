"""CustomerProfile model — THE BEAUTY PASSPORT. Complete digital beauty identity."""
from sqlalchemy import String, Boolean, ForeignKey, Integer, Date, Text, Numeric, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin, generate_uuid


class CustomerProfile(Base, TimestampMixin):
    __tablename__ = "customer_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    preferred_location_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("locations.id"))
    preferred_stylist_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("staff_profiles.id"))

    # ══ HAIR DIAGNOSTICS (AI-populated) ══
    hair_type: Mapped[str | None] = mapped_column(String(50))
    hair_texture: Mapped[str | None] = mapped_column(String(50))
    hair_porosity: Mapped[str | None] = mapped_column(String(50))
    hair_density: Mapped[str | None] = mapped_column(String(50))
    scalp_condition: Mapped[str | None] = mapped_column(String(50))
    hair_damage_level: Mapped[int | None] = mapped_column(Integer)
    natural_hair_color: Mapped[str | None] = mapped_column(String(50))
    current_hair_color: Mapped[str | None] = mapped_column(String(50))
    last_color_date: Mapped[str | None] = mapped_column(Date)
    chemical_history: Mapped[dict | None] = mapped_column(JSON)

    # ══ SKIN DIAGNOSTICS (AI-populated) ══
    skin_type: Mapped[str | None] = mapped_column(String(50))
    skin_tone: Mapped[str | None] = mapped_column(String(50))
    undertone: Mapped[str | None] = mapped_column(String(50))
    primary_skin_concerns: Mapped[list | None] = mapped_column(JSON)
    skin_sensitivity: Mapped[str | None] = mapped_column(String(50))
    spf_usage: Mapped[str | None] = mapped_column(String(50))
    acne_severity: Mapped[int | None] = mapped_column(Integer)
    pigmentation_level: Mapped[int | None] = mapped_column(Integer)
    wrinkle_score: Mapped[int | None] = mapped_column(Integer)
    hydration_estimate: Mapped[str | None] = mapped_column(String(50))

    # ══ LIFESTYLE ══
    city: Mapped[str | None] = mapped_column(String(100))
    local_uv_index: Mapped[float | None] = mapped_column(Numeric(4, 2))
    local_humidity: Mapped[float | None] = mapped_column(Numeric(4, 2))
    local_aqi: Mapped[float | None] = mapped_column(Numeric(6, 2))
    local_temp_celsius: Mapped[float | None] = mapped_column(Numeric(4, 1))
    climate_type: Mapped[str | None] = mapped_column(String(50))
    sun_exposure: Mapped[str | None] = mapped_column(String(50))
    occupation_type: Mapped[str | None] = mapped_column(String(100))
    water_quality: Mapped[str | None] = mapped_column(String(50))
    sleep_quality: Mapped[str | None] = mapped_column(String(50))
    hydration_habit: Mapped[str | None] = mapped_column(String(50))
    stress_level: Mapped[str | None] = mapped_column(String(50))
    diet_type: Mapped[str | None] = mapped_column(String(50))
    upcoming_events: Mapped[list | None] = mapped_column(JSON)

    # ══ ALLERGIES & SAFETY ══
    known_allergies: Mapped[list | None] = mapped_column(JSON)
    product_sensitivities: Mapped[list | None] = mapped_column(JSON)
    patch_tested_on: Mapped[str | None] = mapped_column(Date)
    patch_test_result: Mapped[str | None] = mapped_column(String(50))

    # ══ BEAUTY GOALS ══
    primary_goal: Mapped[str | None] = mapped_column(String(100))
    goal_timeline_weeks: Mapped[int | None] = mapped_column(Integer)
    goal_notes: Mapped[str | None] = mapped_column(Text)
    goal_progress_pct: Mapped[int | None] = mapped_column(Integer)

    # ══ EMOTIONAL PROFILE (SOULSKIN) ══
    dominant_archetype: Mapped[str | None] = mapped_column(String(20))
    archetype_history: Mapped[dict | None] = mapped_column(JSON)
    emotional_sensitivity: Mapped[str | None] = mapped_column(String(50))
    preferred_touch_pressure: Mapped[str | None] = mapped_column(String(50))
    most_booked_mood_state: Mapped[list | None] = mapped_column(JSON)

    # ══ DIGITAL TWIN METADATA ══
    twin_model_url: Mapped[str | None] = mapped_column(Text)
    twin_last_updated: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    twin_skin_timeline: Mapped[dict | None] = mapped_column(JSON)
    simulation_enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    # ══ METADATA ══
    last_scan_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    scan_image_url: Mapped[str | None] = mapped_column(Text)
    beauty_score: Mapped[int | None] = mapped_column(Integer)
    passport_completeness: Mapped[int | None] = mapped_column(Integer)
    total_visits: Mapped[int] = mapped_column(Integer, default=0)
    lifetime_value: Mapped[float | None] = mapped_column(Numeric(12, 2))
    first_visit_date: Mapped[str | None] = mapped_column(Date)
    last_visit_date: Mapped[str | None] = mapped_column(Date)

    # Next-service recommendations (PS-03.05)
    recommended_next_services: Mapped[dict | None] = mapped_column(JSON)
    recommendation_generated_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))

    # Occasion-based planning (PS-03.10)
    occasion_plans: Mapped[dict | None] = mapped_column(JSON)

    # AI profile embedding (pgvector in PostgreSQL, JSON list in SQLite)
    profile_embedding: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # Relationships
    user = relationship("User", back_populates="customer_profile")
    preferred_location = relationship("Location", foreign_keys=[preferred_location_id])

    def __repr__(self) -> str:
        return f"<CustomerProfile user={self.user_id} score={self.beauty_score}>"
