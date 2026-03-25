import asyncio
from app.database import engine
from sqlalchemy import text

async def check():
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT id FROM users WHERE first_name = 'aysha'"))
        row = res.fetchone()
        if row:
            print(f"USER_ID: {row[0]}")

if __name__ == "__main__":
    asyncio.run(check())
