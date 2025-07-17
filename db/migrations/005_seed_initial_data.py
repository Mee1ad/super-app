"""
Migration 005: Seed initial data
"""
from db.migrations.base import Migration, migration_manager
from db.session import database
from apps.diary.models import Mood
from apps.food_planner.models import MealType


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
        # Fix table schemas if needed
        dialect = migration_manager._get_database_dialect()
        
        if dialect == "postgresql":
            # Add updated_at column to moods table if it doesn't exist
            try:
                await self.database.execute("ALTER TABLE moods ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            except Exception:
                pass  # Column might already exist
            
            # Add updated_at column to meal_types table if it doesn't exist
            try:
                await self.database.execute("ALTER TABLE meal_types ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            except Exception:
                pass  # Column might already exist
        else:
            # SQLite - add columns if they don't exist
            try:
                await self.database.execute("ALTER TABLE moods ADD COLUMN updated_at DATETIME DEFAULT DATETIME('now')")
            except Exception:
                pass
            
            try:
                await self.database.execute("ALTER TABLE meal_types ADD COLUMN updated_at DATETIME DEFAULT DATETIME('now')")
            except Exception:
                pass
        
        # Seed moods
        moods_data = [
            {"name": "happy", "emoji": "😊", "color": "#4CAF50"},
            {"name": "sad", "emoji": "😢", "color": "#2196F3"},
            {"name": "excited", "emoji": "🎉", "color": "#FF9800"},
            {"name": "calm", "emoji": "😌", "color": "#4CAF50"},
            {"name": "anxious", "emoji": "😰", "color": "#FF5722"},
            {"name": "angry", "emoji": "😠", "color": "#F44336"},
            {"name": "tired", "emoji": "😴", "color": "#9C27B0"},
            {"name": "neutral", "emoji": "😐", "color": "#607D8B"}
        ]
        
        for mood_data in moods_data:
            existing_mood = await Mood.query.filter(name=mood_data["name"]).first()
            if not existing_mood:
                await Mood.query.create(**mood_data)
        
        # Seed meal types
        meal_types_data = [
            {"name": "breakfast", "emoji": "🌅", "time": "08:00", "description": "Morning meal"},
            {"name": "lunch", "emoji": "🍕", "time": "12:00", "description": "Midday meal"},
            {"name": "dinner", "emoji": "🍽️", "time": "18:00", "description": "Evening meal"},
            {"name": "snack", "emoji": "☕", "time": "15:00", "description": "Light snack"},
            {"name": "dessert", "emoji": "🍰", "time": "20:00", "description": "Sweet treat"}
        ]
        
        for meal_data in meal_types_data:
            existing_meal = await MealType.query.filter(name=meal_data["name"]).first()
            if not existing_meal:
                await MealType.query.create(**meal_data)
    
    async def down(self) -> None:
        """Remove seeded data"""
        await MealType.query.delete()
        await Mood.query.delete() 