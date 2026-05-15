"""AURA — All 32 ORM models in one place.

Import from here for convenience:
    from model import User, Booking, CustomerProfile
"""
from models.user import User
from models.location import Location
from models.staff import StaffProfile
from models.customer import CustomerProfile
from models.service import Service
from models.booking import Booking
from models.soulskin import SoulskinSession
from models.session import ServiceSession
from models.scheduling import SOPTemplate, SOPStep
from models.quality import QualityAssessment
from models.loyalty import LoyaltyProfile, LoyaltyTransaction
from models.feedback import CustomerFeedback
from models.followup import FollowUp
from models.notification import Notification
from models.queue import QueueEntry
from models.inventory import InventoryItem
from models.homecare import HomecarePlan
from models.journey import BeautyJourneyPlan
from models.trend import TrendSignal
from models.knowledge import KnowledgeBase
from models.ar_mirror import ARMirrorSession
from models.digital_twin import DigitalTwin
from models.mood import MoodDetection
from models.waiting_experience import WaitingExperience
from models.climate import ClimateData
from models.handover import StaffHandover
from models.training import TrainingRecord
from models.campaign import Campaign
from models.recommendation import Recommendation

__all__ = [
    "User", "Location", "StaffProfile", "CustomerProfile", "Service", "Booking",
    "SoulskinSession", "ServiceSession", "SOPTemplate", "SOPStep",
    "QualityAssessment", "LoyaltyProfile", "LoyaltyTransaction",
    "CustomerFeedback", "FollowUp", "Notification", "QueueEntry",
    "InventoryItem", "HomecarePlan", "BeautyJourneyPlan", "TrendSignal",
    "KnowledgeBase", "ARMirrorSession", "DigitalTwin", "MoodDetection",
    "WaitingExperience", "ClimateData", "StaffHandover", "TrainingRecord",
    "Campaign", "Recommendation",
]
