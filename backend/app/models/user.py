"""User model — core identity for every person in the system."""
from sqlalchemy import String, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base, TimestampMixin, SoftDeleteMixin, generate_uuid


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    REGIONAL_MANAGER = "regional_manager"
    FRANCHISE_OWNER = "franchise_owner"
    SALON_MANAGER = "salon_manager"
    STYLIST = "stylist"
    CUSTOMER = "customer"


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(String(50), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    preferred_language: Mapped[str] = mapped_column(String(5), default="en")
    push_token: Mapped[str | None] = mapped_column(Text)
    last_login_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    staff_profile = relationship("StaffProfile", back_populates="user", uselist=False)
    customer_profile = relationship("CustomerProfile", back_populates="user", uselist=False)

    def __repr__(self) -> str:
        role_str = self.role.value if hasattr(self.role, 'value') else str(self.role)
        return f"<User {self.email} ({role_str})>"
