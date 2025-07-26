"""
Migration 001: Consolidated initial schema setup
Combines all previous migrations into a single clean initial schema
"""
import logging
import json
from db.migrations.base import Migration, migration_manager
from db.session import models_registry
from core.permissions import DEFAULT_ROLES

logger = logging.getLogger(__name__)


class InitialSchemaConsolidatedMigration(Migration):
    """Consolidated initial database schema migration"""
    
    def get_version(self) -> str:
        return "001"
    
    def get_name(self) -> str:
        return "initial_schema_consolidated"
    
    def get_description(self) -> str:
        return "Create consolidated initial database schema with all tables and seed data"
    
    def get_dependencies(self) -> list[str]:
        return []
    
    async def up(self) -> None:
        """Create consolidated initial schema"""
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
        from apps.food_tracker.models import FoodEntry

        
        # Create all tables using the registry
        await models_registry.create_all()
        
        # Seed default roles
        logger.info("🔄 Seeding default roles...")
        for role_name, role_data in DEFAULT_ROLES.items():
            # Check if role already exists
            existing_role = await self.database.fetch_one(
                "SELECT id FROM roles WHERE name = :name",
                {"name": role_name}
            )
            
            if not existing_role:
                await self.database.execute("""
                    INSERT INTO roles (id, name, description, permissions, created_at, updated_at)
                    VALUES ({uuid_func}, :name, :description, CAST(:permissions AS json), {timestamp_default}, {timestamp_default})
                """.format(uuid_func=uuid_func, timestamp_default=timestamp_default), {
                    "name": role_name,
                    "description": role_data["description"],
                    "permissions": json.dumps(role_data["permissions"])
                })
        logger.info("✅ Default roles seeded")
        
        # Seed initial moods
        logger.info("🔄 Seeding initial moods...")
        moods_data = [
            ("Happy", "😊", "#10B981"),
            ("Sad", "😢", "#EF4444"),
            ("Angry", "😠", "#F59E0B"),
            ("Excited", "🤩", "#8B5CF6"),
            ("Calm", "😌", "#06B6D4"),
            ("Anxious", "😰", "#F97316"),
            ("Grateful", "🙏", "#84CC16"),
            ("Tired", "😴", "#6B7280")
        ]
        
        for name, emoji, color in moods_data:
            # Check if mood already exists
            existing_mood = await self.database.fetch_one(
                "SELECT id FROM moods WHERE name = :name",
                {"name": name}
            )
            
            if not existing_mood:
                await self.database.execute("""
                    INSERT INTO moods (id, name, emoji, color, created_at, updated_at)
                    VALUES ({uuid_func}, :name, :emoji, :color, {timestamp_default}, {timestamp_default})
                """.format(uuid_func=uuid_func, timestamp_default=timestamp_default), {"name": name, "emoji": emoji, "color": color})
        logger.info("✅ Initial moods seeded")
        

        
        # Seed default categories for ideas
        logger.info("🔄 Seeding default categories...")
        categories = [
            ("Personal", "👤"),
            ("Work", "💼"),
            ("Health", "🏥"),
            ("Learning", "📚"),
            ("Travel", "✈️"),
            ("Technology", "💻"),
            ("Creative", "🎨"),
            ("Finance", "💰")
        ]
        
        for name, emoji in categories:
            # Check if category already exists
            existing_category = await self.database.fetch_one(
                "SELECT id FROM categories WHERE name = :name",
                {"name": name}
            )
            
            if not existing_category:
                await self.database.execute("""
                    INSERT INTO categories (id, name, emoji, created_at, updated_at)
                    VALUES ({uuid_func}, :name, :emoji, {timestamp_default}, {timestamp_default})
                """.format(uuid_func=uuid_func, timestamp_default=timestamp_default), {"name": name, "emoji": emoji})
        logger.info("✅ Default categories seeded")
        
        # Create default admin user if not exists
        logger.info("🔄 Creating default admin user...")
        admin_exists = await self.database.fetch_one(
            "SELECT id FROM users WHERE email = :email",
            {"email": "admin@superapp.com"}
        )
        
        if not admin_exists:
            # Get admin role
            admin_role = await self.database.fetch_one(
                "SELECT id FROM roles WHERE name = :name",
                {"name": "admin"}
            )
            
            if admin_role:
                await self.database.execute("""
                    INSERT INTO users (id, email, username, hashed_password, is_active, is_superuser, role, created_at, updated_at)
                    VALUES ({uuid_func}, :email, :username, :hashed_password, :is_active, :is_superuser, :role, {timestamp_default}, {timestamp_default})
                """.format(uuid_func=uuid_func, timestamp_default=timestamp_default), {
                    "email": "admin@superapp.com",
                    "username": "admin",
                    "hashed_password": "hashed_password_placeholder",  # Should be properly hashed in production
                    "is_active": True,
                    "is_superuser": True,
                    "role": admin_role[0]
                })
                logger.info("✅ Default admin user created")
            else:
                logger.warning("⚠️ Admin role not found, skipping admin user creation")
        else:
            logger.info("✅ Default admin user already exists")
        
        logger.info("🎉 Consolidated initial schema setup completed successfully")
    
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