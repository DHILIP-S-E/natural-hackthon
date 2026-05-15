"""Customer mobile auth — phone OTP + Google Sign-In + email/password.

Used by the Flutter mobile app only. All data stored in PostgreSQL.
"""
from datetime import datetime, timedelta, timezone
import random
import string

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_db
from models.user import User, UserRole
from models.customer import CustomerProfile
from utils.auth import create_access_token, create_refresh_token, hash_password, verify_password
from utils.secrets import settings

router = APIRouter(prefix="/auth", tags=["Mobile Auth"])

PHONE_TOKEN_DAYS = 30
OTP_EXPIRY_MINUTES = 10

# In-memory OTP store: phone -> (otp, sent_at)
# In production replace with Redis
_otp_store: dict[str, tuple[str, datetime]] = {}


class SendOtpRequest(BaseModel):
    phone: str

class VerifyOtpRequest(BaseModel):
    phone: str
    otp: str

class PhoneLoginRequest(BaseModel):
    phone: str
    country: str = "IN"

class GoogleLoginRequest(BaseModel):
    google_token: str

class EmailLoginRequest(BaseModel):
    email: str
    password: str

class MobileTokenResponse(BaseModel):
    jwt_token: str
    refresh_token: str
    customer_id: str
    is_new_customer: bool
    face_scan_required: bool


async def _get_or_create_customer(
    db: AsyncSession,
    phone: str | None = None,
    email: str | None = None,
    first_name: str = "",
    last_name: str = "",
) -> MobileTokenResponse:
    query = select(User)
    if phone:
        query = query.where(User.phone == phone)
    elif email:
        query = query.where(User.email == email)
    else:
        raise HTTPException(status_code=400, detail="phone or email required")

    result = await db.execute(query)
    user = result.scalar_one_or_none()
    is_new = user is None

    if is_new:
        user = User(
            email=email,
            phone=phone,
            password_hash="",
            role=UserRole.CUSTOMER,
            first_name=first_name,
            last_name=last_name,
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
    cp = profile_result.scalar_one_or_none()
    face_scan_required = cp is None or not cp.face_analysis_data

    access, refresh = _make_tokens(str(user.id))
    return MobileTokenResponse(
        jwt_token=access,
        refresh_token=refresh,
        customer_id=str(user.id),
        is_new_customer=is_new,
        face_scan_required=face_scan_required,
    )


def _make_tokens(user_id: str) -> tuple[str, str]:
    data = {"sub": user_id}
    access = create_access_token(
        data, expires_delta=timedelta(days=PHONE_TOKEN_DAYS)
    )
    refresh = create_refresh_token(data)
    return access, refresh


@router.post("/send-otp")
async def send_otp(req: SendOtpRequest):
    """Send 6-digit OTP to phone number."""
    phone = req.phone.strip()
    if not phone.startswith("+"):
        phone = f"+91{phone}"

    otp = "".join(random.choices(string.digits, k=6))
    _otp_store[phone] = (otp, datetime.now(timezone.utc))

    # Send via Twilio if configured, else log for testing
    if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
        try:
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=f"Your Natural AURA OTP is: {otp}. Valid for {OTP_EXPIRY_MINUTES} minutes.",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone,
            )
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"SMS send failed: {exc}") from exc
    else:
        # Dev mode — OTP printed in backend logs
        print(f"[DEV] OTP for {phone}: {otp}")

    return {"success": True, "message": f"OTP sent to {phone}"}


@router.post("/verify-otp", response_model=MobileTokenResponse)
async def verify_otp(req: VerifyOtpRequest, db: AsyncSession = Depends(get_db)):
    """Verify OTP and return JWT. Creates account if new customer."""
    phone = req.phone.strip()
    if not phone.startswith("+"):
        phone = f"+91{phone}"

    entry = _otp_store.get(phone)
    if not entry:
        raise HTTPException(status_code=400, detail="No OTP sent to this number. Request a new one.")

    stored_otp, sent_at = entry
    if datetime.now(timezone.utc) - sent_at > timedelta(minutes=OTP_EXPIRY_MINUTES):
        _otp_store.pop(phone, None)
        raise HTTPException(status_code=400, detail="OTP expired. Request a new one.")

    if req.otp != stored_otp:
        raise HTTPException(status_code=400, detail="Invalid OTP.")

    _otp_store.pop(phone, None)
    return await _get_or_create_customer(phone=phone, db=db)


@router.post("/login-email", response_model=MobileTokenResponse)
async def login_email(req: EmailLoginRequest, db: AsyncSession = Depends(get_db)):
    """Email + password login for customers."""
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    profile_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.user_id == user.id)
    )
    cp = profile_result.scalar_one_or_none()
    face_scan_required = cp is None or not cp.face_analysis_data
    access, refresh = _make_tokens(str(user.id))
    return MobileTokenResponse(
        jwt_token=access,
        refresh_token=refresh,
        customer_id=str(user.id),
        is_new_customer=False,
        face_scan_required=face_scan_required,
    )


@router.post("/login-phone", response_model=MobileTokenResponse)
async def login_phone(req: PhoneLoginRequest, db: AsyncSession = Depends(get_db)):
    """Direct phone login without OTP (kept for dev/testing). Use verify-otp in production."""
    phone = req.phone.strip()
    if not phone.startswith("+"):
        phone = f"+91{phone}"
    return await _get_or_create_customer(phone=phone, db=db)


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

    return await _get_or_create_customer(
        email=email, first_name=given_name, last_name=family_name, db=db
    )


@router.get("/check-session")
async def check_session(db: AsyncSession = Depends(get_db)):
    """Lightweight session check — actual JWT validation is done by middleware."""
    return {"valid": True}
