"""AURA Models — Package init. Imports all models + enums for Alembic autodiscovery."""
from app.models.user import User, UserRole
from app.models.location import Location
from app.models.staff import StaffProfile, SkillLevel, AttritionRisk
from app.models.customer import CustomerProfile
from app.models.service import Service, SOP
from app.models.booking import Booking, BookingStatus, PaymentStatus, PaymentMethod, BookingSource
from app.models.session import ServiceSession, SessionStatus
from app.models.quality import QualityAssessment, SkillAssessment, AssessmentType
from app.models.soulskin import SoulskinSession
from app.models.mood import MoodDetection
from app.models.digital_twin import DigitalBeautyTwin
from app.models.ar_mirror import ARMirrorSession, MirrorSessionType, MirrorInitiator
from app.models.journey import BeautyJourneyPlan
from app.models.climate import ClimateRecommendation
from app.models.queue import SmartQueueEntry, QueueStatus, WalkInSource
from app.models.trend import TrendSignal, TrendTrajectory, TrendLongevity
from app.models.feedback import CustomerFeedback, Sentiment, FeedbackSource
from app.models.homecare import HomecarePlan
from app.models.training import TrainingRecord, TrainingType
from app.models.notification import Notification, NotificationChannel, NotificationPriority
from app.models.knowledge import KnowledgeBaseEntry

__all__ = [
    # Models
    "User", "Location", "StaffProfile", "CustomerProfile",
    "Service", "SOP", "Booking", "ServiceSession",
    "QualityAssessment", "SkillAssessment",
    "SoulskinSession", "MoodDetection", "DigitalBeautyTwin",
    "ARMirrorSession", "BeautyJourneyPlan", "ClimateRecommendation",
    "SmartQueueEntry", "TrendSignal", "CustomerFeedback",
    "HomecarePlan", "TrainingRecord", "Notification",
    "KnowledgeBaseEntry",
    # Enums
    "UserRole", "SkillLevel", "AttritionRisk",
    "BookingStatus", "PaymentStatus", "PaymentMethod", "BookingSource",
    "SessionStatus", "AssessmentType",
    "MirrorSessionType", "MirrorInitiator",
    "QueueStatus", "WalkInSource",
    "TrendTrajectory", "TrendLongevity",
    "Sentiment", "FeedbackSource",
    "TrainingType",
    "NotificationChannel", "NotificationPriority",
]
