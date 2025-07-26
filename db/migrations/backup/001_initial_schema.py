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
        
        # Import all models to ensure they are registered
        from apps.todo.models import List, Task, ShoppingItem
        from apps.auth.models import User, Role
        from apps.changelog.models import ChangelogEntry, ChangelogView
        from apps.ideas.models import Category, Idea
        from apps.diary.models import Mood, DiaryEntry

        
        # Create all tables using the registry (including roles table)
        await models_registry.create_all()
    
    async def down(self) -> None:
        """Drop all tables"""
        # Drop all tables in reverse dependency order
        tables_to_drop = [
            "changelog_views",
            "changelog_entries", 
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