"""Auth dependencies & RBAC — FastAPI dependency injection for all routes."""
from typing import List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, enum_val
from app.models.user import User, UserRole
from app.utils.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Decode JWT and return the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        if user_id is None or token_type != "access":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id, User.is_deleted == False))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def require_roles(allowed_roles: List[UserRole]):
    """Dependency factory — restricts endpoint to specific roles."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role_str = enum_val(current_user.role)
        allowed_strs = [enum_val(r) for r in allowed_roles]
        if user_role_str not in allowed_strs:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user_role_str}' does not have access to this resource",
            )
        return current_user
    return role_checker


def require_role(allowed_roles):
    """Dependency factory — accepts role name strings or UserRole enums.

    Usage: Depends(require_role(["stylist", "salon_manager"]))
    """
    resolved = []
    for r in allowed_roles:
        if isinstance(r, UserRole):
            resolved.append(r)
        else:
            try:
                resolved.append(UserRole(r))
            except ValueError:
                pass
    return require_roles(resolved)


def require_any_staff():
    """Allow any non-customer role."""
    return require_roles([
        UserRole.SUPER_ADMIN, UserRole.REGIONAL_MANAGER,
        UserRole.FRANCHISE_OWNER, UserRole.SALON_MANAGER, UserRole.STYLIST,
    ])


async def check_customer_ownership(user: User, customer_id: str, db: AsyncSession):
    """Check if the user owns this customer profile or is staff.

    Customers can only access their own data.
    Staff can access any customer data (based on their location/region).
    """
    if enum_val(user.role) == UserRole.CUSTOMER.value:
        from app.models.customer import CustomerProfile
        result = await db.execute(
            select(CustomerProfile).where(CustomerProfile.user_id == user.id, CustomerProfile.id == customer_id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own data",
            )


async def check_booking_ownership(user: User, booking_id: str, db: AsyncSession):
    """Check if user owns this booking or is staff."""
    if enum_val(user.role) == UserRole.CUSTOMER.value:
        from app.models.booking import Booking
        from app.models.customer import CustomerProfile
        # Get customer profile for this user
        cp_result = await db.execute(
            select(CustomerProfile).where(CustomerProfile.user_id == user.id)
        )
        cp = cp_result.scalar_one_or_none()
        if not cp:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No customer profile")
        # Check booking belongs to this customer
        bk_result = await db.execute(
            select(Booking).where(Booking.id == booking_id, Booking.customer_id == cp.id)
        )
        if not bk_result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only access your own bookings")
