"""Loyalty & Rewards models — personalized loyalty program."""
from sqlalchemy import String, Boolean, ForeignKey, Integer, Text, Numeric, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, TimestampMixin, generate_uuid


class LoyaltyProgram(Base, TimestampMixin):
    __tablename__ = "loyalty_programs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customer_profiles.id"), unique=True)
    tier: Mapped[str | None] = mapped_column(String(20))
    total_points: Mapped[int] = mapped_column(Integer, default=0)
    redeemable_points: Mapped[int] = mapped_column(Integer, default=0)
    lifetime_points_earned: Mapped[int] = mapped_column(Integer, default=0)
    tier_expires_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    referral_code: Mapped[str | None] = mapped_column(String(20), unique=True)
    referred_by: Mapped[str | None] = mapped_column(String(36))

    def __repr__(self) -> str:
        return f"<LoyaltyProgram tier={self.tier} pts={self.total_points}>"


class LoyaltyTransaction(Base, TimestampMixin):
    __tablename__ = "loyalty_transactions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    loyalty_program_id: Mapped[str] = mapped_column(String(36), ForeignKey("loyalty_programs.id"), nullable=False)
    booking_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("bookings.id"))
    transaction_type: Mapped[str | None] = mapped_column(String(20))
    points: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str | None] = mapped_column(Text)
    extra_data: Mapped[dict | None] = mapped_column(JSON)

    def __repr__(self) -> str:
        return f"<LoyaltyTransaction {self.transaction_type} {self.points}pts>"


class PersonalizedOffer(Base, TimestampMixin):
    __tablename__ = "personalized_offers"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customer_profiles.id"), nullable=False)
    offer_type: Mapped[str | None] = mapped_column(String(50))
    title: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    discount_percent: Mapped[float | None] = mapped_column(Numeric(5, 2))
    valid_from: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    valid_until: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    service_ids: Mapped[list | None] = mapped_column(JSON)
    is_redeemed: Mapped[bool] = mapped_column(Boolean, default=False)
    redeemed_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    ai_reason: Mapped[str | None] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<PersonalizedOffer {self.title}>"
