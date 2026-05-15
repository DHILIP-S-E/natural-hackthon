"""Auth schemas — login, register, token responses."""
from typing import Optional
from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    password: str
    first_name: str
    last_name: str
    preferred_language: str = "en"
    city: Optional[str] = None
    preferred_location_id: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserBrief"


class UserBrief(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    role: str
    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    preferred_language: Optional[str] = None
    avatar_url: Optional[str] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


# ── Role Management Schemas ──

class RoleInfo(BaseModel):
    """Single role details."""
    name: str
    value: str
    description: str
    user_count: int = 0

    model_config = {"from_attributes": True}


class RoleAssign(BaseModel):
    """Assign a role to a user."""
    user_id: str
    role: str


class AdminUserCreate(BaseModel):
    """Admin creates a user with any role."""
    email: EmailStr
    phone: Optional[str] = None
    password: str
    first_name: str
    last_name: str
    role: str
    preferred_language: str = "en"
    location_id: Optional[str] = None


class AdminUserUpdate(BaseModel):
    """Admin updates a user."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    preferred_language: Optional[str] = None


class UserDetail(BaseModel):
    """Full user detail for admin views."""
    id: str
    email: str
    phone: Optional[str] = None
    first_name: str
    last_name: str
    role: str
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    preferred_language: str = "en"
    created_at: Optional[str] = None
    last_login_at: Optional[str] = None

    model_config = {"from_attributes": True}


# Update forward reference
TokenResponse.model_rebuild()
