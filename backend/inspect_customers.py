import asyncio
from app.database import engine
from sqlalchemy import text

async def check():
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT u.first_name, u.last_name, cp.id FROM customer_profiles cp JOIN users u ON cp.user_id = u.id"))
        for row in res.fetchall():
            print(f"Name: {row[0]} {row[1]} | ID: {row[2]}")

if __name__ == "__main__":
    asyncio.run(check())
