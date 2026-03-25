import asyncio
from app.database import engine
from sqlalchemy import text

async def verify():
    customer_id = "617c87d8-bc2f-4c8c-8504-21ab13bf9f2d"
    async with engine.begin() as conn:
        # Update
        await conn.execute(text("""
            UPDATE customer_profiles 
            SET hair_type = 'Straight/Fine',
                skin_type = 'Oily/Combination',
                stress_level = 'high',
                diet_type = 'Vegetarian',
                beauty_score = 78,
                dominant_archetype = 'phoenix'
            WHERE id = :id
        """), {"id": customer_id})
        
        # Verify
        res = await conn.execute(text("SELECT hair_type, skin_type, beauty_score FROM customer_profiles WHERE id = :id"), {"id": customer_id})
        row = res.fetchone()
        print(f"VERIFIED DB STATE: {row}")

if __name__ == "__main__":
    asyncio.run(verify())
