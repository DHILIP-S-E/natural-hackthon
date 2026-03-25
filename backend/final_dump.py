import asyncio
import json
from app.database import engine
from sqlalchemy import text

async def check():
    id = "57f5b294-6160-4a57-8613-f663ca9a5f68"
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT * from customer_profiles where id=:id"), {"id": id})
        row = res.fetchone()
        if row:
            data = {k: str(v) for k, v in zip(res.keys(), row)}
            with open('aysha_profile_final.json', 'w') as f:
                json.dump(data, f, indent=2)
            print("REFRESHED")

if __name__ == "__main__":
    asyncio.run(check())
