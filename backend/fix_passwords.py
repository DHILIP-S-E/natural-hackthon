"""Fix demo user passwords to match Aura@2026."""
import asyncio
from sqlalchemy import select, update
from app.database import engine, async_session_factory
from app.models.user import User
from app.utils.security import hash_password

PASSWORD = "Aura@2026"

async def fix():
    new_hash = hash_password(PASSWORD)
    async with async_session_factory() as db:
        result = await db.execute(select(User).where(User.is_deleted == False))
        users = result.scalars().all()
        print(f"Found {len(users)} users in DB")
        for u in users:
            u.password_hash = new_hash
            print(f"  Updated: {u.email} ({u.role})")
        await db.commit()
        print(f"\nAll {len(users)} user passwords set to '{PASSWORD}'")

if __name__ == "__main__":
    asyncio.run(fix())
