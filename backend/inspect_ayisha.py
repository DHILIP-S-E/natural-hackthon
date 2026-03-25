import asyncio
import json
from app.database import engine
from sqlalchemy import text

async def check():
    async with engine.begin() as conn:
        res = await conn.execute(text("""
            SELECT 
                cp.id, 
                u.first_name, 
                cp.city, 
                cp.diet_type, 
                cp.stress_level, 
                cp.hair_type,
                cp.skin_type,
                cp.beauty_score
            FROM customer_profiles cp
            JOIN users u ON cp.user_id = u.id
            WHERE u.first_name ILIKE '%ayisha%'
            LIMIT 1
        """))
        row = res.fetchone()
        if row:
            data = {
                "id": row[0],
                "name": row[1],
                "city": row[2],
                "diet_type": row[3],
                "stress_level": row[4],
                "hair_type": row[5],
                "skin_type": row[6],
                "beauty_score": row[7]
            }
            print(json.dumps(data, indent=2))
        else:
            print("Ayisha profile not found.")

if __name__ == "__main__":
    asyncio.run(check())
