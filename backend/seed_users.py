"""Seed demo users with roles matching the login page demo accounts."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from db.db import engine, async_session_factory, Base
from models.user import User, UserRole
from utils.auth import hash_password

PASSWORD = "Aura@2026"

USERS = [
    {"email": "super@aura.in",    "role": UserRole.SUPER_ADMIN,       "first_name": "Rajesh",  "last_name": "Kumar",    "phone": "+919000000001"},
    {"email": "regional@aura.in", "role": UserRole.REGIONAL_MANAGER,  "first_name": "Lakshmi", "last_name": "Nair",     "phone": "+919000000002"},
    {"email": "owner@aura.in",    "role": UserRole.FRANCHISE_OWNER,   "first_name": "Arun",    "last_name": "Venkatesh","phone": "+919000000003"},
    {"email": "manager@aura.in",  "role": UserRole.SALON_MANAGER,     "first_name": "Deepa",   "last_name": "Ramesh",   "phone": "+919000000004"},
    {"email": "stylist@aura.in",  "role": UserRole.STYLIST,           "first_name": "Meena",   "last_name": "Sundaram", "phone": "+919000000005"},
    {"email": "customer@aura.in", "role": UserRole.CUSTOMER,          "first_name": "Priya",   "last_name": "Sharma",   "phone": "+919000000006"},
]


async def seed():
    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    pw_hash = hash_password(PASSWORD)

    async with async_session_factory() as db:
        created = 0
        skipped = 0

        for u in USERS:
            from sqlalchemy import select
            result = await db.execute(select(User).where(User.email == u["email"]))
            existing = result.scalar_one_or_none()

            if existing:
                # Update password in case it changed
                existing.password_hash = pw_hash
                existing.is_active = True
                existing.is_verified = True
                print(f"  UPDATED  {u['email']} ({u['role'].value})")
                skipped += 1
            else:
                user = User(
                    email=u["email"],
                    phone=u["phone"],
                    password_hash=pw_hash,
                    role=u["role"],
                    first_name=u["first_name"],
                    last_name=u["last_name"],
                    is_active=True,
                    is_verified=True,
                )
                db.add(user)
                print(f"  CREATED  {u['email']} ({u['role'].value})")
                created += 1

        await db.commit()

    print()
    print(f"Done — {created} created, {skipped} updated")
    print(f"Password for all accounts: {PASSWORD}")
    print()
    print("Demo accounts:")
    for u in USERS:
        print(f"  {u['email']:30s}  {u['role'].value}")


if __name__ == "__main__":
    asyncio.run(seed())
