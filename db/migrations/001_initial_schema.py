"""
Migration 001: Initial schema setup
"""
from db.migrations.base import Migration, migration_manager
from db.session import models_registry


class InitialSchemaMigration(Migration):
    """Initial database schema migration"""
    
    def get_version(self) -> str:
        return "001"
    
    def get_name(self) -> str:
        return "initial_schema"
    
    def get_description(self) -> str:
        return "Create initial database schema with core tables"
    
    def get_dependencies(self) -> list[str]:
        return []
    
    async def up(self) -> None:
        """Create initial schema"""
        dialect = migration_manager._get_database_dialect()
        uuid_func = migration_manager._get_uuid_function()
        timestamp_default = migration_manager._get_timestamp_default()
        
        if dialect == "postgresql":
            # Create PostgreSQL extension
            await self.database.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
        
        # Create roles table first (this one needs manual creation)
        await self.database.execute(f'''
            CREATE TABLE IF NOT EXISTS roles (
                id UUID PRIMARY KEY DEFAULT {uuid_func},
                name VARCHAR(255) UNIQUE NOT NULL,
                description TEXT,
                permissions TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT {timestamp_default},
                updated_at TIMESTAMP DEFAULT {timestamp_default}
            )
        ''')
        
        # Import all models to ensure they are registered
        from apps.todo.models import List, Task, ShoppingItem
        from apps.auth.models import User, Role
        from apps.changelog.models import ChangelogEntry, ChangelogView
        from apps.ideas.models import Category, Idea
        from apps.diary.models import Mood, DiaryEntry
        from apps.food_planner.models import MealType, FoodEntry
        
        # Create all other tables using the registry (including moods and meal_types)
        await models_registry.create_all()
    
    async def down(self) -> None:
        """Drop all tables"""
        # Drop all tables in reverse dependency order
        tables_to_drop = [
            "changelog_views",
            "changelog_entries", 
            "food_entries",
            "meal_types",
            "diary_entries",
            "moods",
            "ideas",
            "categories",
            "shopping_items",
            "tasks",
            "lists",
            "users",
            "roles"
        ]
        
        for table in tables_to_drop:
            try:
                await self.database.execute(f"DROP TABLE IF EXISTS {table}")
            except Exception as e:
                # Ignore errors if table doesn't exist
                pass 