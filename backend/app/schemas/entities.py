"""AURA Schemas — Pydantic V2 models for all entities."""
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime, date
from uuid import UUID


# ── Users ──
class UserBrief(BaseModel):
    id: UUID
    email: str
    first_name: str
    last_name: str
    role: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    preferred_language: Optional[str] = None


# ── Locations ──
class LocationCreate(BaseModel):
    name: str
    code: str
    city: str
    state: str
    region: str = "South India"
    address: str
    phone: Optional[str] = None
    seating_capacity: int = 8
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    monthly_revenue_target: float = 500000

class LocationOut(BaseModel):
    id: UUID
    name: str
    code: str
    city: str
    state: str
    address: str
    is_active: bool
    smart_mirror_enabled: bool
    soulskin_enabled: bool
    seating_capacity: Optional[int] = None

    class Config:
        from_attributes = True


# ── Staff ──
class StaffCreate(BaseModel):
    user_id: UUID
    location_id: UUID
    employee_id: str
    designation: str = "Stylist"
    specializations: list[str] = []
    skill_level: str = "L1"
    years_experience: float = 0
    bio: Optional[str] = None

class StaffUpdate(BaseModel):
    designation: Optional[str] = None
    specializations: Optional[list[str]] = None
    skill_level: Optional[str] = None
    is_available: Optional[bool] = None
    bio: Optional[str] = None

class StaffOut(BaseModel):
    id: UUID
    user_id: UUID
    employee_id: str
    designation: str
    skill_level: str
    specializations: list[str] = []
    is_available: bool
    current_rating: float = 0
    total_services_done: int = 0
    soulskin_certified: bool = False
    attrition_risk_label: Optional[str] = None

    class Config:
        from_attributes = True


# ── Customers ──
class CustomerOut(BaseModel):
    id: UUID
    user_id: UUID
    beauty_score: int = 50
    passport_completeness: int = 0
    hair_type: Optional[str] = None
    skin_type: Optional[str] = None
    skin_tone: Optional[str] = None
    dominant_archetype: Optional[str] = None
    total_visits: int = 0
    lifetime_value: float = 0
    known_allergies: list[str] = []
    city: Optional[str] = None
    primary_goal: Optional[str] = None
    goal_progress_pct: int = 0

    class Config:
        from_attributes = True

class CustomerUpdate(BaseModel):
    hair_type: Optional[str] = None
    hair_texture: Optional[str] = None
    skin_type: Optional[str] = None
    skin_tone: Optional[str] = None
    undertone: Optional[str] = None
    primary_skin_concerns: Optional[list[str]] = None
    known_allergies: Optional[list[str]] = None
    stress_level: Optional[str] = None
    diet_type: Optional[str] = None
    primary_goal: Optional[str] = None
    city: Optional[str] = None


# ── Services ──
class ServiceCreate(BaseModel):
    name: str
    category: str
    subcategory: Optional[str] = None
    description: Optional[str] = None
    short_description: str = ""
    duration_minutes: int
    base_price: float
    skill_required: str = "L1"
    is_chemical: bool = False
    ar_preview_available: bool = False
    tags: list[str] = []

class ServiceOut(BaseModel):
    id: UUID
    name: str
    category: str
    subcategory: Optional[str] = None
    short_description: str
    duration_minutes: int
    base_price: float
    skill_required: str
    is_chemical: bool = False
    ar_preview_available: bool = False
    tags: list[str] = []

    class Config:
        from_attributes = True


# ── Bookings ──
class BookingCreate(BaseModel):
    customer_id: UUID
    location_id: UUID
    stylist_id: UUID
    service_id: UUID
    scheduled_at: datetime
    base_price: float
    source: str = "app"
    notes: Optional[str] = None

class BookingOut(BaseModel):
    id: UUID
    booking_number: str
    status: str
    scheduled_at: datetime
    base_price: float
    final_price: float
    payment_status: str
    source: str

    class Config:
        from_attributes = True


# ── Sessions ──
class SessionCreate(BaseModel):
    booking_id: UUID
    sop_id: Optional[UUID] = None
    soulskin_session_id: Optional[UUID] = None
    steps_total: Optional[int] = None

class SessionOut(BaseModel):
    id: UUID
    booking_id: UUID
    status: str
    current_step: int = 1
    steps_total: Optional[int] = None
    steps_completed: Optional[list[int]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    quality_score: Optional[float] = None
    sop_compliance_pct: Optional[float] = None

    class Config:
        from_attributes = True


# ── SOULSKIN ──
class SoulskinCreate(BaseModel):
    customer_id: UUID
    booking_id: Optional[UUID] = None
    question_1_song: Optional[str] = None
    question_2_colour: Optional[str] = None
    question_3_word: Optional[str] = None

class SoulskinOut(BaseModel):
    id: UUID
    archetype: Optional[str] = None
    soul_reading: Optional[str] = None
    session_completed: bool = False

    class Config:
        from_attributes = True


# ── Quality ──
class QualityAssessmentCreate(BaseModel):
    booking_id: UUID
    session_id: Optional[UUID] = None
    stylist_id: UUID
    location_id: UUID
    service_id: UUID
    sop_compliance_score: float = 0
    timing_score: float = 0
    customer_rating: Optional[int] = None
    manager_rating: Optional[int] = None

class QualityOut(BaseModel):
    id: UUID
    booking_id: UUID
    overall_score: float
    sop_compliance_score: float
    timing_score: float
    customer_rating: Optional[int] = None
    soulskin_alignment_score: Optional[float] = None

    class Config:
        from_attributes = True

class SkillAssessmentCreate(BaseModel):
    staff_id: UUID
    assessment_type: str = "ai"
    service_category: Optional[str] = None
    skill_area: Optional[str] = None
    current_level: str = "L1"
    score: float = 0
    rubric_scores: Optional[dict] = None

class SkillAssessmentOut(BaseModel):
    id: UUID
    staff_id: UUID
    assessment_type: str
    current_level: str
    score: float
    recommended_training: Optional[list[str]] = None

    class Config:
        from_attributes = True


# ── Trends ──
class TrendOut(BaseModel):
    id: UUID
    trend_name: str
    description: str
    service_category: str
    overall_signal_strength: float
    trajectory: str
    longevity_label: str
    is_active: bool

    class Config:
        from_attributes = True


# ── Climate ──
class ClimateOut(BaseModel):
    id: UUID
    city: str
    temperature_celsius: float
    humidity_pct: float
    uv_index: float
    aqi: float
    weather_condition: str
    hair_recommendations: dict
    skin_recommendations: dict
    is_alert: bool

    class Config:
        from_attributes = True


# ── Queue ──
class QueueCreate(BaseModel):
    customer_name: str
    customer_phone: str
    service_id: Optional[UUID] = None
    location_id: UUID
    walk_in_source: str = "in_person"

class QueueOut(BaseModel):
    id: UUID
    customer_name: str
    position_in_queue: int
    status: str
    estimated_wait_mins: int = 0

    class Config:
        from_attributes = True


# ── Feedback ──
class FeedbackCreate(BaseModel):
    customer_id: UUID
    stylist_id: UUID
    location_id: UUID
    service_id: UUID
    booking_id: Optional[UUID] = None
    overall_rating: int = Field(ge=1, le=5)
    service_rating: int = Field(ge=1, le=5)
    stylist_rating: int = Field(ge=1, le=5)
    soulskin_experience_rating: Optional[int] = Field(default=None, ge=1, le=5)
    comment: Optional[str] = None
    would_recommend: bool = True

class FeedbackOut(BaseModel):
    id: UUID
    overall_rating: int
    comment: Optional[str] = None
    sentiment: Optional[str] = None

    class Config:
        from_attributes = True


# ── Homecare ──
class HomecareCreate(BaseModel):
    customer_id: UUID
    booking_id: Optional[UUID] = None
    soulskin_archetype: Optional[str] = None
    plan_duration_weeks: int = 4
    hair_routine: dict = {}
    skin_routine: dict = {}
    dos: Optional[list[str]] = None
    donts: Optional[list[str]] = None

class HomecareOut(BaseModel):
    id: UUID
    customer_id: UUID
    soulskin_archetype: Optional[str] = None
    plan_duration_weeks: Optional[int] = None
    whatsapp_sent: bool = False

    class Config:
        from_attributes = True


# ── Notifications ──
class NotificationOut(BaseModel):
    id: UUID
    title: Optional[str] = None
    body: Optional[str] = None
    notification_type: Optional[str] = None
    channel: Optional[str] = None
    is_read: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Training ──
class TrainingCreate(BaseModel):
    staff_id: UUID
    training_name: str
    training_type: str = "online"
    service_category: Optional[str] = None
    provider: Optional[str] = None
    trainer_name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    hours_completed: float = 0
    cost_to_company: float = 0
    passed: bool = False
    score: Optional[float] = None
    includes_soulskin: bool = False

class TrainingOut(BaseModel):
    id: UUID
    training_name: str
    training_type: str
    passed: bool
    score: Optional[float] = None
    hours_completed: float

    class Config:
        from_attributes = True


# ── Journey ──
class JourneyCreate(BaseModel):
    customer_id: UUID
    plan_duration_weeks: int = 12
    primary_goal: Optional[str] = None
    milestones: Optional[list] = None

class JourneyOut(BaseModel):
    id: UUID
    customer_id: UUID
    plan_duration_weeks: Optional[int] = None
    primary_goal: Optional[str] = None
    whatsapp_sent: bool = False

    class Config:
        from_attributes = True


# ── AR Mirror ──
class MirrorSessionCreate(BaseModel):
    customer_id: UUID
    location_id: UUID
    session_type: str = "hairstyle"

class MirrorSessionOut(BaseModel):
    id: UUID
    session_type: str
    saved_images: list = []

    class Config:
        from_attributes = True


# ── Mood ──
class MoodCreate(BaseModel):
    customer_id: UUID
    booking_id: Optional[UUID] = None
    detected_emotion: str = "neutral"
    emotion_confidence: float = 0.8
    energy_level: str = "medium"
    consent_given: bool = False

class MoodOut(BaseModel):
    id: UUID
    detected_emotion: str
    emotion_confidence: float
    energy_level: Optional[str] = None
    recommended_archetype: Optional[str] = None

    class Config:
        from_attributes = True


# ── Digital Twin ──
class TwinCreate(BaseModel):
    customer_id: UUID
    model_data_url: Optional[str] = None
    texture_url: Optional[str] = None
    consent_given: bool = False

class TwinOut(BaseModel):
    id: UUID
    customer_id: UUID
    model_data_url: Optional[str] = None
    is_active: bool
    consent_given: bool = False

    class Config:
        from_attributes = True
