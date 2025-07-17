#!/usr/bin/env python3
"""
Fix meal types by adding missing emoji and time fields
"""
import asyncio
import sys
import os
import platform

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from db.session import database

async def fix_meal_types():
    """Update existing meal types with missing emoji and time fields"""
    try:
        await database.connect()
        print("✅ Connected to database")
        
        # Update meal types with emoji and time
        meal_type_updates = [
            ("breakfast", "🌅", "08:00"),
            ("lunch", "🍕", "12:00"),
            ("dinner", "🍽️", "18:00"),
            ("snack", "☕", "15:00"),
            ("dessert", "🍰", "20:00")
        ]
        
        for meal_name, emoji, time in meal_type_updates:
            await database.execute("""
                UPDATE meal_types 
                SET emoji = :emoji, time = :time 
                WHERE name = :name
            """, {
                "name": meal_name,
                "emoji": emoji,
                "time": time
            })
            print(f"✅ Updated {meal_name} with emoji: {emoji}, time: {time}")
        
        print("\n🎉 Meal types updated successfully!")
        
    except Exception as e:
        print(f"❌ Error updating meal types: {e}")
        raise
    finally:
        await database.disconnect()

if __name__ == "__main__":
    asyncio.run(fix_meal_types()) 