"""Roles & Admin User Management router — full CRUD for roles and users."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db, enum_val
from app.models.user import User, UserRole
from app.dependencies import get_current_user, require_roles
from app.schemas.common import APIResponse
from app.schemas.auth import (
    RoleInfo, RoleAssign, AdminUserCreate, AdminUserUpdate, UserDetail,
)
from app.utils.security import hash_password

router = APIRouter(prefix="/roles", tags=["Roles & User Management"])

# ── Role descriptions for each UserRole ──
ROLE_DESCRIPTIONS = {
    UserRole.SUPER_ADMIN: "Full system access. Manages all locations, staff, and settings.",
    UserRole.REGIONAL_MANAGER: "Manages multiple locations within an assigned region.",
    UserRole.FRANCHISE_OWNER: "Owns one or more franchise locations. Views business analytics.",
    UserRole.SALON_MANAGER: "Manages a single salon location. Handles daily operations.",
    UserRole.STYLIST: "Performs services, views assigned bookings and quality scores.",
    UserRole.CUSTOMER: "Books services, manages Beauty Passport, views recommendations.",
}

# Roles allowed to manage other roles
ADMIN_ROLES = [UserRole.SUPER_ADMIN, UserRole.REGIONAL_MANAGER]

# Which roles each admin role can assign
ASSIGNABLE_ROLES = {
    UserRole.SUPER_ADMIN.value: [r.value for r in UserRole],
    UserRole.REGIONAL_MANAGER.value: [
        UserRole.FRANCHISE_OWNER.value, UserRole.SALON_MANAGER.value,
        UserRole.STYLIST.value, UserRole.CUSTOMER.value,
    ],
    UserRole.FRANCHISE_OWNER.value: [
        UserRole.SALON_MANAGER.value, UserRole.STYLIST.value,
    ],
    UserRole.SALON_MANAGER.value: [
        UserRole.STYLIST.value,
    ],
}


def _validate_role(role_str: str) -> UserRole:
    """Validate a role string and return the UserRole enum."""
    try:
        return UserRole(role_str)
    except ValueError:
        valid = [r.value for r in UserRole]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role '{role_str}'. Valid roles: {valid}",
        )


def _check_can_assign(admin_user: User, target_role: str):
    """Check if the admin user is allowed to assign the target role."""
    admin_role_str = enum_val(admin_user.role)
    assignable = ASSIGNABLE_ROLES.get(admin_role_str, [])
    if target_role not in assignable:
        raise HTTPException(
            status_code=403,
            detail=f"Role '{admin_role_str}' cannot assign role '{target_role}'",
        )


def _user_to_detail(u: User) -> dict:
    """Convert a User model to a detail dict."""
    return {
        "id": u.id,
        "email": u.email,
        "phone": u.phone,
        "first_name": u.first_name,
        "last_name": u.last_name,
        "role": enum_val(u.role),
        "is_active": u.is_active,
        "is_verified": u.is_verified,
        "avatar_url": u.avatar_url,
        "preferred_language": u.preferred_language,
        "created_at": u.created_at.isoformat() if u.created_at else None,
        "last_login_at": str(u.last_login_at) if u.last_login_at else None,
    }


# ═══════════════════════════════════════════
# ROLE ENDPOINTS
# ═══════════════════════════════════════════

@router.get("", response_model=APIResponse)
async def list_roles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all available roles with user counts."""
    roles = []
    for role in UserRole:
        count_q = select(func.count()).select_from(User).where(
            User.role == role.value, User.is_deleted == False
        )
        count = (await db.execute(count_q)).scalar() or 0
        roles.append({
            "name": role.name,
            "value": role.value,
            "description": ROLE_DESCRIPTIONS.get(role, ""),
            "user_count": count,
        })
    return APIResponse(success=True, data=roles)


@router.get("/{role_value}", response_model=APIResponse)
async def get_role(
    role_value: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get details for a specific role including its users."""
    role_enum = _validate_role(role_value)

    count_q = select(func.count()).select_from(User).where(
        User.role == role_enum.value, User.is_deleted == False
    )
    count = (await db.execute(count_q)).scalar() or 0

    # Get users with this role (first 50)
    users_q = select(User).where(
        User.role == role_enum.value, User.is_deleted == False
    ).order_by(User.created_at.desc()).limit(50)
    result = await db.execute(users_q)
    users = result.scalars().all()

    return APIResponse(
        success=True,
        data={
            "role": {
                "name": role_enum.name,
                "value": role_enum.value,
                "description": ROLE_DESCRIPTIONS.get(role_enum, ""),
                "user_count": count,
            },
            "users": [
                {
                    "id": u.id,
                    "full_name": f"{u.first_name or ''} {u.last_name or ''}".strip(),
                    "email": u.email,
                    "is_active": u.is_active,
                    "created_at": u.created_at.isoformat() if u.created_at else None,
                }
                for u in users
            ],
        },
    )


@router.get("/{role_value}/permissions", response_model=APIResponse)
async def get_role_permissions(
    role_value: str,
    current_user: User = Depends(get_current_user),
):
    """Get permissions/capabilities for a specific role."""
    role_enum = _validate_role(role_value)

    # Define permissions per role
    permissions = {
        UserRole.SUPER_ADMIN.value: {
            "can_manage_users": True,
            "can_manage_locations": True,
            "can_manage_staff": True,
            "can_manage_services": True,
            "can_manage_roles": True,
            "can_view_analytics": True,
            "can_manage_sops": True,
            "can_manage_training": True,
            "can_manage_quality": True,
            "can_delete_data": True,
            "assignable_roles": ASSIGNABLE_ROLES.get(UserRole.SUPER_ADMIN.value, []),
        },
        UserRole.REGIONAL_MANAGER.value: {
            "can_manage_users": True,
            "can_manage_locations": False,
            "can_manage_staff": True,
            "can_manage_services": False,
            "can_manage_roles": True,
            "can_view_analytics": True,
            "can_manage_sops": False,
            "can_manage_training": True,
            "can_manage_quality": True,
            "can_delete_data": False,
            "assignable_roles": ASSIGNABLE_ROLES.get(UserRole.REGIONAL_MANAGER.value, []),
        },
        UserRole.FRANCHISE_OWNER.value: {
            "can_manage_users": False,
            "can_manage_locations": False,
            "can_manage_staff": True,
            "can_manage_services": False,
            "can_manage_roles": False,
            "can_view_analytics": True,
            "can_manage_sops": False,
            "can_manage_training": True,
            "can_manage_quality": True,
            "can_delete_data": False,
            "assignable_roles": ASSIGNABLE_ROLES.get(UserRole.FRANCHISE_OWNER.value, []),
        },
        UserRole.SALON_MANAGER.value: {
            "can_manage_users": False,
            "can_manage_locations": True,
            "can_manage_staff": True,
            "can_manage_services": False,
            "can_manage_roles": False,
            "can_view_analytics": True,
            "can_manage_sops": True,
            "can_manage_training": False,
            "can_manage_quality": True,
            "can_delete_data": False,
            "assignable_roles": ASSIGNABLE_ROLES.get(UserRole.SALON_MANAGER.value, []),
        },
        UserRole.STYLIST.value: {
            "can_manage_users": False,
            "can_manage_locations": False,
            "can_manage_staff": False,
            "can_manage_services": False,
            "can_manage_roles": False,
            "can_view_analytics": False,
            "can_manage_sops": False,
            "can_manage_training": False,
            "can_manage_quality": False,
            "can_delete_data": False,
            "assignable_roles": [],
        },
        UserRole.CUSTOMER.value: {
            "can_manage_users": False,
            "can_manage_locations": False,
            "can_manage_staff": False,
            "can_manage_services": False,
            "can_manage_roles": False,
            "can_view_analytics": False,
            "can_manage_sops": False,
            "can_manage_training": False,
            "can_manage_quality": False,
            "can_delete_data": False,
            "assignable_roles": [],
        },
    }

    return APIResponse(
        success=True,
        data={
            "role": role_enum.value,
            "permissions": permissions.get(role_enum.value, {}),
        },
    )


# ═══════════════════════════════════════════
# ROLE ASSIGNMENT
# ═══════════════════════════════════════════

@router.post("/assign", response_model=APIResponse)
async def assign_role(
    req: RoleAssign,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
):
    """Assign a role to a user (admin only)."""
    target_role = _validate_role(req.role)
    _check_can_assign(current_user, target_role.value)

    result = await db.execute(
        select(User).where(User.id == req.user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    old_role = enum_val(user.role)
    user.role = target_role.value

    # If upgrading to staff role, ensure staff profile exists
    if target_role in (UserRole.STYLIST, UserRole.SALON_MANAGER) and old_role == UserRole.CUSTOMER.value:
        from app.models.staff import StaffProfile
        existing = await db.execute(
            select(StaffProfile).where(StaffProfile.user_id == user.id)
        )
        if not existing.scalar_one_or_none():
            staff = StaffProfile(
                user_id=user.id,
                employee_id=f"EMP-{user.id[:8].upper()}",
                designation=target_role.value.replace("_", " ").title(),
            )
            db.add(staff)

    return APIResponse(
        success=True,
        data={"user_id": user.id, "old_role": old_role, "new_role": target_role.value},
        message=f"Role changed from '{old_role}' to '{target_role.value}'",
    )


# ═══════════════════════════════════════════
# ADMIN USER CRUD
# ═══════════════════════════════════════════

@router.get("/users/all", response_model=APIResponse)
async def admin_list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
):
    """List all users with filtering — admin only."""
    query = select(User).where(User.is_deleted == False)

    if role and role != "All":
        role_enum = _validate_role(role)
        query = query.where(User.role == role_enum.value)

    if is_active is not None:
        query = query.where(User.is_active == is_active)

    if search:
        search_term = f"%{search}%"
        from sqlalchemy import or_
        query = query.where(
            or_(
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term),
                User.email.ilike(search_term),
                User.phone.ilike(search_term),
            )
        )

    total_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(total_q)).scalar() or 0

    query = query.order_by(User.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    users = result.scalars().all()

    return APIResponse(
        success=True,
        data={
            "users": [_user_to_detail(u) for u in users],
            "total": total,
            "page": page,
            "per_page": per_page,
        },
        message=f"{total} users found",
    )


@router.get("/users/{user_id}", response_model=APIResponse)
async def admin_get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
):
    """Get full user detail — admin only."""
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    data = _user_to_detail(user)

    # Attach staff profile if applicable
    staff_role_values = [UserRole.STYLIST.value, UserRole.SALON_MANAGER.value,
                         UserRole.FRANCHISE_OWNER.value, UserRole.REGIONAL_MANAGER.value]
    if enum_val(user.role) in staff_role_values:
        from app.models.staff import StaffProfile
        sp_result = await db.execute(
            select(StaffProfile).where(StaffProfile.user_id == user.id)
        )
        sp = sp_result.scalar_one_or_none()
        if sp:
            data["staff_profile"] = {
                "id": sp.id,
                "employee_id": sp.employee_id,
                "designation": sp.designation,
                "location_id": sp.location_id,
                "skill_level": enum_val(sp.skill_level) if sp.skill_level else None,
                "is_available": sp.is_available,
            }

    # Attach customer profile if customer
    if enum_val(user.role) == UserRole.CUSTOMER.value:
        from app.models.customer import CustomerProfile
        cp_result = await db.execute(
            select(CustomerProfile).where(CustomerProfile.user_id == user.id)
        )
        cp = cp_result.scalar_one_or_none()
        if cp:
            data["customer_profile"] = {
                "id": cp.id,
                "beauty_score": cp.beauty_score,
                "total_visits": cp.total_visits,
                "city": cp.city,
            }

    return APIResponse(success=True, data=data)


@router.post("/users", response_model=APIResponse)
async def admin_create_user(
    req: AdminUserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
):
    """Create a new user with any role — admin only."""
    target_role = _validate_role(req.role)
    _check_can_assign(current_user, target_role.value)

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
        role=target_role.value,
        first_name=req.first_name,
        last_name=req.last_name,
        preferred_language=req.preferred_language,
        is_verified=True,
        is_active=True,
    )
    db.add(user)
    await db.flush()

    # Auto-create staff profile for staff roles
    if target_role in (UserRole.STYLIST, UserRole.SALON_MANAGER,
                       UserRole.FRANCHISE_OWNER, UserRole.REGIONAL_MANAGER):
        from app.models.staff import StaffProfile
        staff = StaffProfile(
            user_id=user.id,
            location_id=req.location_id,
            employee_id=f"EMP-{user.id[:8].upper()}",
            designation=target_role.value.replace("_", " ").title(),
        )
        db.add(staff)

    # Auto-create customer profile for customer role
    if target_role == UserRole.CUSTOMER:
        from app.models.customer import CustomerProfile
        profile = CustomerProfile(user_id=user.id)
        db.add(profile)

    return APIResponse(
        success=True,
        data={"id": user.id, "email": user.email, "role": target_role.value},
        message=f"User created with role '{target_role.value}'",
    )


@router.patch("/users/{user_id}", response_model=APIResponse)
async def admin_update_user(
    user_id: str,
    req: AdminUserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
):
    """Update user details — admin only."""
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent editing yourself to avoid lockout
    if user.id == current_user.id and req.role and req.role != enum_val(current_user.role):
        raise HTTPException(status_code=400, detail="Cannot change your own role")

    if user.id == current_user.id and req.is_active is False:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")

    updates = req.model_dump(exclude_unset=True)

    # Handle role change
    if "role" in updates:
        target_role = _validate_role(updates["role"])
        _check_can_assign(current_user, target_role.value)
        updates["role"] = target_role.value

    # Handle email uniqueness
    if "email" in updates and updates["email"] != user.email:
        existing = await db.execute(select(User).where(User.email == updates["email"]))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already in use")

    # Handle phone uniqueness
    if "phone" in updates and updates["phone"] and updates["phone"] != user.phone:
        existing = await db.execute(select(User).where(User.phone == updates["phone"]))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Phone number already in use")

    for field, value in updates.items():
        setattr(user, field, value)

    return APIResponse(
        success=True,
        data=_user_to_detail(user),
        message="User updated",
    )


@router.patch("/users/{user_id}/activate", response_model=APIResponse)
async def admin_activate_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
):
    """Activate a deactivated user — admin only."""
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = True
    return APIResponse(success=True, message="User activated")


@router.patch("/users/{user_id}/deactivate", response_model=APIResponse)
async def admin_deactivate_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
):
    """Deactivate a user — admin only."""
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")

    user.is_active = False
    return APIResponse(success=True, message="User deactivated")


@router.delete("/users/{user_id}", response_model=APIResponse)
async def admin_delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN])),
):
    """Soft-delete a user — SUPER_ADMIN only."""
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    user.is_deleted = True
    user.deleted_at = datetime.now(timezone.utc)
    user.is_active = False

    return APIResponse(
        success=True,
        message=f"User '{user.email}' soft-deleted",
    )


@router.post("/users/{user_id}/reset-password", response_model=APIResponse)
async def admin_reset_password(
    user_id: str,
    new_password: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(ADMIN_ROLES)),
):
    """Reset a user's password — admin only."""
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = hash_password(new_password)

    return APIResponse(success=True, message="Password reset successfully")
