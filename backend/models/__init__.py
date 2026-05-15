"""AURA Models — Package init. Imports all models + enums for Alembic autodiscovery."""
from models.user import User, UserRole
from models.location import Location
from models.staff import StaffProfile, SkillLevel, AttritionRisk
from models.customer import CustomerProfile
from models.service import Service, SOP
from models.booking import Booking, BookingStatus, PaymentStatus, PaymentMethod, BookingSource
from models.session import ServiceSession, SessionStatus
from models.quality import QualityAssessment, SkillAssessment, AssessmentType
from models.soulskin import SoulskinSession
from models.mood import MoodDetection
from models.digital_twin import DigitalBeautyTwin
from models.ar_mirror import ARMirrorSession, MirrorSessionType, MirrorInitiator
from models.journey import BeautyJourneyPlan
from models.climate import ClimateRecommendation
from models.queue import SmartQueueEntry, QueueStatus, WalkInSource
from models.trend import TrendSignal, TrendTrajectory, TrendLongevity
from models.feedback import CustomerFeedback, Sentiment, FeedbackSource
from models.homecare import HomecarePlan
from models.training import TrainingRecord, TrainingType
from models.notification import Notification, NotificationChannel, NotificationPriority
from models.knowledge import KnowledgeBaseEntry
from models.inventory import InventoryItem, InventoryUsageLog
from models.campaign import Campaign, CompetitiveIntel, CelebrityTrendSource
from models.scheduling import StaffSchedule, FloatRequest
from models.recommendation import ServiceRecommendation
from models.loyalty import LoyaltyProgram, LoyaltyTransaction

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
    "LoyaltyProgram", "LoyaltyTransaction",
    "InventoryItem", "InventoryUsageLog",
    "Campaign", "ServiceRecommendation",
    "StaffSchedule", "FloatRequest",
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
