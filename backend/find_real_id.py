import asyncio
from app.database import engine
from sqlalchemy import text

async def list_all():
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT cp.id, u.first_name, u.last_name FROM customer_profiles cp JOIN users u ON cp.user_id = u.id"))
        for row in res.fetchall():
            print(f"PROFILE: {row[0]} -> {row[1]} {row[2]}")

if __name__ == "__main__":
    asyncio.run(list_all())
