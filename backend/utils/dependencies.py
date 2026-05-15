"""FastAPI dependency injection — auth and RBAC."""
from fastapi import Depends, HTTPException, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_db, enum_val
from utils.auth import (
    get_current_user,
    require_role,
    require_roles,
    require_any_staff,
    decode_token,
    oauth2_scheme,
)


async def get_optional_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Like get_current_user but returns None instead of raising 401."""
    if not token:
        return None
    try:
        from models.user import User
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id or payload.get("type") != "access":
            return None
        result = await db.execute(
            select(User).where(User.id == user_id, User.is_deleted == False)
        )
        return result.scalar_one_or_none()
    except (JWTError, Exception):
        return None


async def check_customer_ownership(user, customer_id: str, db: AsyncSession):
    from models.customer import CustomerProfile
    if enum_val(user.role) == "customer":
        result = await db.execute(
            select(CustomerProfile).where(
                CustomerProfile.user_id == user.id,
                CustomerProfile.id == customer_id,
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only access your own data")


async def check_booking_ownership(user, booking_id: str, db: AsyncSession):
    from models.booking import Booking
    from models.customer import CustomerProfile
    if enum_val(user.role) == "customer":
        cp = (await db.execute(
            select(CustomerProfile).where(CustomerProfile.user_id == user.id)
        )).scalar_one_or_none()
        if not cp:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No customer profile")
        if not (await db.execute(
            select(Booking).where(Booking.id == booking_id, Booking.customer_id == cp.id)
        )).scalar_one_or_none():
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only access your own bookings")


__all__ = [
    "get_current_user", "get_optional_user",
    "require_role", "require_roles", "require_any_staff",
    "check_customer_ownership", "check_booking_ownership",
]
