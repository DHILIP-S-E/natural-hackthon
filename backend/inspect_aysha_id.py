import asyncio
import json
from app.database import engine
from sqlalchemy import text

async def check():
    async with engine.begin() as conn:
        res = await conn.execute(text("""
            SELECT * FROM customer_profiles WHERE id = '13420ae3-1422-485b-8613-f663ca9a5f68'
        """))
        row = res.fetchone()
        if row:
            # Get column names
            keys = res.keys()
            data = {k: str(v) for k, v in zip(keys, row)}
            print(json.dumps(data, indent=2))
        else:
            print("Profile not found.")

if __name__ == "__main__":
    asyncio.run(check())
