"""Customer mobile auth — phone login (no OTP) + Google Sign-In.

Used by the Flutter mobile app only. All data stored in PostgreSQL.
"""
from datetime import datetime, timedelta, timezone
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_db
from models.user import User, UserRole
from models.customer import CustomerProfile
from utils.auth import create_access_token, create_refresh_token
from utils.secrets import settings

router = APIRouter(prefix="/auth", tags=["Mobile Auth"])

PHONE_TOKEN_DAYS = 30


class PhoneLoginRequest(BaseModel):
    phone: str
    country: str = "IN"


class GoogleLoginRequest(BaseModel):
    google_token: str


class MobileTokenResponse(BaseModel):
    jwt_token: str
    refresh_token: str
    customer_id: str
    is_new_customer: bool
    face_scan_required: bool


def _make_tokens(user_id: str) -> tuple[str, str]:
    data = {"sub": user_id}
    access = create_access_token(
        data, expires_delta=timedelta(days=PHONE_TOKEN_DAYS)
    )
    refresh = create_refresh_token(data)
    return access, refresh


@router.post("/login-phone", response_model=MobileTokenResponse)
async def login_phone(req: PhoneLoginRequest, db: AsyncSession = Depends(get_db)):
    """Phone number login with no OTP — creates account if new customer."""
    phone = req.phone.strip()
    if not phone.startswith("+"):
        phone = f"+91{phone}"

    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()
    is_new = user is None

    if is_new:
        user = User(
            email=None,
            phone=phone,
            password_hash="",
            role=UserRole.CUSTOMER,
            first_name="",
            last_name="",
            is_verified=True,
        )
        db.add(user)
        await db.flush()

        profile = CustomerProfile(user_id=user.id)
        db.add(profile)
        await db.flush()
    else:
        user.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(user)

    # Check if face scan has been done
    profile_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.user_id == user.id)
    )
    customer_profile = profile_result.scalar_one_or_none()
    face_scan_required = customer_profile is None or not customer_profile.face_analysis_data

    access, refresh = _make_tokens(str(user.id))

    return MobileTokenResponse(
        jwt_token=access,
        refresh_token=refresh,
        customer_id=str(user.id),
        is_new_customer=is_new,
        face_scan_required=face_scan_required,
    )


@router.post("/google-login", response_model=MobileTokenResponse)
async def google_login(req: GoogleLoginRequest, db: AsyncSession = Depends(get_db)):
    """Google Sign-In — verifies ID token via Google, creates/fetches account."""
    import httpx

    # Verify Google ID token
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://oauth2.googleapis.com/tokeninfo",
                params={"id_token": req.google_token},
                timeout=10,
            )
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid Google token")
        token_info = resp.json()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Google auth unavailable: {exc}") from exc

    email = token_info.get("email", "")
    google_sub = token_info.get("sub", "")
    given_name = token_info.get("given_name", "")
    family_name = token_info.get("family_name", "")

    if not email:
        raise HTTPException(status_code=400, detail="Google token has no email")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    is_new = user is None

    if is_new:
        user = User(
            email=email,
            phone=None,
            password_hash="",
            role=UserRole.CUSTOMER,
            first_name=given_name,
            last_name=family_name,
            is_verified=True,
        )
        db.add(user)
        await db.flush()

        profile = CustomerProfile(user_id=user.id)
        db.add(profile)
        await db.flush()
    else:
        user.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(user)

    profile_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.user_id == user.id)
    )
    customer_profile = profile_result.scalar_one_or_none()
    face_scan_required = customer_profile is None or not customer_profile.face_analysis_data

    access, refresh = _make_tokens(str(user.id))

    return MobileTokenResponse(
        jwt_token=access,
        refresh_token=refresh,
        customer_id=str(user.id),
        is_new_customer=is_new,
        face_scan_required=face_scan_required,
    )


@router.get("/check-session")
async def check_session(db: AsyncSession = Depends(get_db)):
    """Lightweight session check — actual JWT validation is done by middleware."""
    return {"valid": True}
