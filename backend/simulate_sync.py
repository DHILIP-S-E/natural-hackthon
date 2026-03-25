import asyncio
from app.database import engine
from sqlalchemy import text

async def simulate():
    # Aysha's ID from previous inspection
    customer_id = "617c87d8-bc2f-4c8c-8504-21ab13bf9f2d"
    
    async with engine.begin() as conn:
        # Update profile with some data to simulate successful AI sync
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
        print(f"Simulated update for {customer_id}")

if __name__ == "__main__":
    asyncio.run(simulate())
