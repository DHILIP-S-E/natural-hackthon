import asyncio
import json
from app.database import engine
from sqlalchemy import text

async def check():
    async with engine.begin() as conn:
        res = await conn.execute(text("""
            SELECT * FROM customer_profiles cp
            JOIN users u ON cp.user_id = u.id
            WHERE u.first_name = 'aysha'
        """))
        row = res.fetchone()
        if row:
            keys = res.keys()
            data = {k: str(v) for k, v in zip(keys, row)}
            with open('aysha_profile.json', 'w') as f:
                json.dump(data, f, indent=2)
            print("Wrote to aysha_profile.json")
        else:
            print("Not found.")

if __name__ == "__main__":
    asyncio.run(check())
