import asyncio
from app.database import engine
from sqlalchemy import text

async def check():
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT u.first_name, cp.id from customer_profiles cp join users u on cp.user_id = u.id"))
        for row in res.fetchall():
            print(f"FOUND: {row[0]} -> {row[1]}")

if __name__ == "__main__":
    asyncio.run(check())
