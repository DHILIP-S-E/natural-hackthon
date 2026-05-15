"""Auth router — register, login, logout, refresh, profile, users list, Google OAuth."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from db.db import get_db, enum_val
from models.user import User, UserRole
from models.customer import CustomerProfile
from schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse, UserBrief, UserUpdate, PasswordChange,
)
from schemas.common import APIResponse
from utils.auth import hash_password, verify_password, create_access_token, create_refresh_token
from utils.dependencies import get_current_user
from utils.secrets import settings


class GoogleAuthRequest(BaseModel):
    id_token: str

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=APIResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new customer account."""
    # Check existing email
    existing = await db.execute(select(User).where(User.email == req.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check existing phone
    if req.phone:
        existing_phone = await db.execute(select(User).where(User.phone == req.phone))
        if existing_phone.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Phone number already registered")

    user = User(
        email=req.email,
        phone=req.phone,
        password_hash=hash_password(req.password),
        role=UserRole.CUSTOMER,
        first_name=req.first_name,
        last_name=req.last_name,
        preferred_language=req.preferred_language,
        is_verified=False,
    )
    db.add(user)
    await db.flush()

    # Create customer profile with optional city and preferred location
    profile = CustomerProfile(
        user_id=user.id,
        city=req.city,
        preferred_location_id=req.preferred_location_id,
    )
    db.add(profile)
    await db.flush()

    # Auto-enroll customer into AURA Points loyalty program
    try:
        from models.loyalty import LoyaltyProgram
        from db.db import generate_uuid
        import random, string
        code = "AURA" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        lp = LoyaltyProgram(
            id=generate_uuid(),
            customer_id=profile.id,
            tier="bronze",
            total_points=100,          # 100 welcome points
            redeemable_points=100,
            lifetime_points_earned=100,
            referral_code=code,
        )
        db.add(lp)
        from models.loyalty import LoyaltyTransaction
        welcome_txn = LoyaltyTransaction(
            id=generate_uuid(),
            loyalty_program_id=lp.id,
            transaction_type="earn",
            points=100,
            description="Welcome to AURA! 🎉 Signup bonus",
        )
        db.add(welcome_txn)
    except Exception:
        pass

    access_token = create_access_token({"sub": user.id, "role": enum_val(user.role)})
    refresh_token = create_refresh_token({"sub": user.id})

    return APIResponse(
        success=True,
        data=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserBrief(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                role=enum_val(user.role),
                avatar_url=user.avatar_url,
            ),
        ).model_dump(),
        message="Registration successful",
    )


@router.post("/login", response_model=APIResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return tokens."""
    result = await db.execute(
        select(User).where(User.email == req.email, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    # Update last login
    user.last_login_at = datetime.now(timezone.utc)

    access_token = create_access_token({"sub": user.id, "role": enum_val(user.role)})
    refresh_token = create_refresh_token({"sub": user.id})

    return APIResponse(
        success=True,
        data=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserBrief(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                role=enum_val(user.role),
                avatar_url=user.avatar_url,
            ),
        ).model_dump(),
        message="Login successful",
    )


@router.get("/me", response_model=APIResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return APIResponse(
        success=True,
        data=UserBrief(
            id=current_user.id,
            email=current_user.email,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            role=enum_val(current_user.role),
            avatar_url=current_user.avatar_url,
        ).model_dump(),
    )


@router.patch("/me", response_model=APIResponse)
async def update_me(
    updates: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user profile."""
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    return APIResponse(success=True, message="Profile updated")


@router.patch("/me/password", response_model=APIResponse)
async def change_password(
    req: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change current user password."""
    if not verify_password(req.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current_user.password_hash = hash_password(req.new_password)
    return APIResponse(success=True, message="Password changed")


@router.post("/refresh", response_model=APIResponse)
async def refresh_token(token: str, db: AsyncSession = Depends(get_db)):
    """Exchange refresh token for new access + refresh tokens."""
    from utils.auth import decode_token
    from jose import JWTError
    try:
        payload = decode_token(token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    result = await db.execute(select(User).where(User.id == user_id, User.is_deleted == False))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    new_access = create_access_token({"sub": user.id, "role": enum_val(user.role)})
    new_refresh = create_refresh_token({"sub": user.id})

    return APIResponse(success=True, data={
        "access_token": new_access,
        "refresh_token": new_refresh,
        "user": UserBrief(
            id=user.id, email=user.email,
            first_name=user.first_name, last_name=user.last_name,
            role=enum_val(user.role), avatar_url=user.avatar_url,
        ).model_dump(),
    }, message="Token refreshed")


@router.post("/me/push-token", response_model=APIResponse)
async def register_push_token(
    push_token: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Register PWA push notification token."""
    current_user.push_token = push_token
    return APIResponse(success=True, message="Push token registered")


@router.post("/google", response_model=APIResponse)
async def google_signin(req: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    """Sign in or register using a Google ID token (from Firebase / Google OAuth)."""
    import httpx
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": req.id_token},
            timeout=10,
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    info = resp.json()

    # Verify audience when client ID is configured
    if settings.GOOGLE_CLIENT_ID and info.get("aud") != settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=401, detail="Token audience mismatch")

    google_uid = info.get("sub")
    email = info.get("email")
    if not email or not google_uid:
        raise HTTPException(status_code=400, detail="Google account missing email")

    name = info.get("name", "")
    picture = info.get("picture")

    result = await db.execute(
        select(User).where(
            User.is_deleted == False,
            or_(User.google_id == google_uid, User.email == email),
        )
    )
    user = result.scalar_one_or_none()

    if user:
        if not user.google_id:
            user.google_id = google_uid
        if picture and not user.avatar_url:
            user.avatar_url = picture
        user.last_login_at = datetime.now(timezone.utc)
    else:
        name_parts = name.split(" ", 1)
        first = name_parts[0] if name_parts else email.split("@")[0]
        last = name_parts[1] if len(name_parts) > 1 else ""

        user = User(
            email=email,
            google_id=google_uid,
            password_hash="!google_oauth",
            role=UserRole.CUSTOMER,
            first_name=first,
            last_name=last,
            avatar_url=picture,
            is_verified=True,
        )
        db.add(user)
        await db.flush()

        profile = CustomerProfile(user_id=user.id)
        db.add(profile)
        await db.flush()

        try:
            from models.loyalty import LoyaltyProgram, LoyaltyTransaction
            from db.db import generate_uuid
            import random, string
            code = "AURA" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
            lp = LoyaltyProgram(
                id=generate_uuid(), customer_id=profile.id, tier="bronze",
                total_points=100, redeemable_points=100, lifetime_points_earned=100,
                referral_code=code,
            )
            db.add(lp)
            db.add(LoyaltyTransaction(
                id=generate_uuid(), loyalty_program_id=lp.id,
                transaction_type="earn", points=100,
                description="Welcome to AURA! 🎉 Signup bonus",
            ))
        except Exception:
            pass

    await db.commit()
    await db.refresh(user)

    access_token = create_access_token({"sub": user.id, "role": enum_val(user.role)})
    refresh_token = create_refresh_token({"sub": user.id})

    return APIResponse(
        success=True,
        data=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserBrief(
                id=user.id, email=user.email,
                first_name=user.first_name, last_name=user.last_name,
                role=enum_val(user.role), avatar_url=user.avatar_url,
            ),
        ).model_dump(),
        message="Google sign-in successful",
    )


@router.post("/logout", response_model=APIResponse)
async def logout():
    """Logout — client should discard tokens."""
    return APIResponse(success=True, message="Logged out successfully")


@router.get("/users", response_model=APIResponse)
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    role: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all users — admin only."""
    admin_roles = [UserRole.SUPER_ADMIN, UserRole.REGIONAL_MANAGER]
    user_role_str = enum_val(current_user.role)
    if user_role_str not in [enum_val(r) for r in admin_roles]:
        raise HTTPException(status_code=403, detail="Admin access required")

    query = select(User).where(User.is_deleted == False)
    if role and role != "All":
        try:
            valid_role = UserRole(role)
            query = query.where(User.role == valid_role.value)
        except ValueError:
            pass

    total_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(total_q)).scalar() or 0

    query = query.order_by(User.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    users = result.scalars().all()

    return APIResponse(
        success=True,
        data=[
            {
                "id": u.id,
                "full_name": f"{u.first_name or ''} {u.last_name or ''}".strip() or u.email,
                "email": u.email,
                "role": enum_val(u.role),
                "status": "active" if u.is_active else "inactive",
                "phone": u.phone,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ],
        message=f"{total} users found",
    )


@router.post("/forgot-password", response_model=APIResponse)
async def forgot_password(email: str, db: AsyncSession = Depends(get_db)):
    """Send password reset OTP to email."""
    import hashlib, secrets
    result = await db.execute(select(User).where(User.email == email, User.is_deleted == False))
    user = result.scalar_one_or_none()
    if not user:
        # Don't reveal whether email exists
        return APIResponse(success=True, message="If the email exists, a reset OTP has been sent")

    # Generate 6-digit OTP, hash and store
    otp = str(secrets.randbelow(900000) + 100000)
    otp_hash = hashlib.sha256(otp.encode()).hexdigest()
    user.push_token = f"otp:{otp_hash}"

    # Send OTP via SMTP email
    from services.email_service import send_otp_email
    email_sent = await send_otp_email(email, otp, "password reset")

    return APIResponse(
        success=True,
        data={"_demo_otp": otp} if not email_sent else None,
        message="Reset OTP sent to your email" if email_sent else "Reset OTP generated (email not configured)",
    )


@router.post("/reset-password", response_model=APIResponse)
async def reset_password(email: str, otp: str, new_password: str, db: AsyncSession = Depends(get_db)):
    """Reset password using OTP."""
    import hashlib
    result = await db.execute(select(User).where(User.email == email, User.is_deleted == False))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid request")

    # Verify OTP
    otp_hash = hashlib.sha256(otp.encode()).hexdigest()
    if not user.push_token or user.push_token != f"otp:{otp_hash}":
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    user.password_hash = hash_password(new_password)
    user.push_token = None
    await db.commit()
    return APIResponse(success=True, message="Password reset successfully")


@router.post("/send-otp", response_model=APIResponse)
async def send_otp(phone: str, db: AsyncSession = Depends(get_db)):
    """Send OTP for phone verification."""
    import secrets
    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()
    if not user:
        return APIResponse(success=True, message="If the phone exists, an OTP has been sent")

    import hashlib
    otp = str(secrets.randbelow(900000) + 100000)
    otp_hash = hashlib.sha256(otp.encode()).hexdigest()
    user.push_token = f"phone_otp:{otp_hash}"

    # Send OTP via email (SMTP) since no Twilio
    from services.email_service import send_otp_email
    email_sent = False
    if user.email:
        email_sent = await send_otp_email(user.email, otp, "phone verification")

    await db.commit()
    return APIResponse(
        success=True,
        data={"_demo_otp": otp} if not email_sent else None,
        message="OTP sent to your email" if email_sent else "OTP generated (email not configured)",
    )


@router.post("/verify-otp", response_model=APIResponse)
async def verify_otp(phone: str, otp: str, db: AsyncSession = Depends(get_db)):
    """Verify phone OTP and mark user as verified."""
    import hashlib
    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid request")

    otp_hash = hashlib.sha256(otp.encode()).hexdigest()
    if not user.push_token or user.push_token != f"phone_otp:{otp_hash}":
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    user.is_verified = True
    user.push_token = None
    await db.commit()
    return APIResponse(success=True, message="Phone verified successfully")


@router.post("/verify-email", response_model=APIResponse)
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    """Verify email address using token."""
    from utils.auth import decode_token
    from jose import JWTError
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    user.is_verified = True
    return APIResponse(success=True, message="Email verified successfully")


@router.post("/me/avatar", response_model=APIResponse)
async def upload_avatar(
    avatar_url: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user avatar URL (in production: handle file upload to S3)."""
    current_user.avatar_url = avatar_url
    return APIResponse(success=True, message="Avatar updated")
