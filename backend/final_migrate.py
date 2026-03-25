import asyncio
from app.database import engine
from sqlalchemy import text

async def final():
    id = "57f5b294-6160-4a57-8613-f663ca9a5f68"
    async with engine.begin() as conn:
        await conn.execute(text("""
            UPDATE customer_profiles 
            SET hair_type = 'Straight/Fine',
                skin_type = 'Oily/Combination',
                stress_level = 'high',
                diet_type = 'Vegetarian',
                beauty_score = 78,
                dominant_archetype = 'phoenix'
            WHERE id = :id
        """), {"id": id})
        print("MIGRATED AYSHA PROFILE")

if __name__ == "__main__":
    asyncio.run(final())
