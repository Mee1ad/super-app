"""
Migration 005: Seed initial data
"""
from db.migrations.base import Migration
from db.session import database


class SeedInitialDataMigration(Migration):
    """Seed initial data like moods and meal types"""
    
    def get_version(self) -> str:
        return "005"
    
    def get_name(self) -> str:
        return "seed_initial_data"
    
    def get_description(self) -> str:
        return "Seed initial data including moods and meal types"
    
    def get_dependencies(self) -> list[str]:
        return ["001"]
    
    async def up(self) -> None:
        """Seed initial data"""
        # Seed moods
        moods = [
            ("happy", "Happy and content"),
            ("sad", "Sad or down"),
            ("excited", "Excited and energetic"),
            ("calm", "Calm and peaceful"),
            ("anxious", "Anxious or worried"),
            ("angry", "Angry or frustrated"),
            ("tired", "Tired or exhausted"),
            ("neutral", "Neutral or indifferent")
        ]
        
        for mood_name, mood_description in moods:
            existing_mood = await database.fetch_one(
                "SELECT id FROM moods WHERE name = :name",
                {"name": mood_name}
            )
            
            if not existing_mood:
                await database.execute("""
                    INSERT INTO moods (name, description)
                    VALUES (:name, :description)
                """, {
                    "name": mood_name,
                    "description": mood_description
                })
        
        # Seed meal types
        meal_types = [
            ("breakfast", "🌅", "08:00", "Morning meal"),
            ("lunch", "🍕", "12:00", "Midday meal"),
            ("dinner", "🍽️", "18:00", "Evening meal"),
            ("snack", "☕", "15:00", "Light snack"),
            ("dessert", "🍰", "20:00", "Sweet treat")
        ]
        
        for meal_name, meal_emoji, meal_time, meal_description in meal_types:
            existing_meal = await database.fetch_one(
                "SELECT id FROM meal_types WHERE name = :name",
                {"name": meal_name}
            )
            
            if not existing_meal:
                await database.execute("""
                    INSERT INTO meal_types (name, emoji, time, description)
                    VALUES (:name, :emoji, :time, :description)
                """, {
                    "name": meal_name,
                    "emoji": meal_emoji,
                    "time": meal_time,
                    "description": meal_description
                })
    
    async def down(self) -> None:
        """Remove seeded data"""
        await database.execute("DELETE FROM meal_types")
        await database.execute("DELETE FROM moods") 