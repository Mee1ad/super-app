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
        from apps.food_planner.models import MealType, FoodEntry
        
        # Create all tables using the registry
        await models_registry.create_all()
        
        # Seed default roles
        logger.info("🔄 Seeding default roles...")
        for role_name, role_data in DEFAULT_ROLES.items():
            await self.database.execute("""
                INSERT INTO roles (name, description, permissions)
                VALUES (:name, :description, CAST(:permissions AS json))
            """, {
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
            await self.database.execute("""
                INSERT INTO moods (name, emoji, color)
                VALUES (:name, :emoji, :color)
            """, {"name": name, "emoji": emoji, "color": color})
        logger.info("✅ Initial moods seeded")
        
        # Seed meal types
        logger.info("🔄 Seeding meal types...")
        meal_types = [
            ("Breakfast", "🌅", "#F59E0B"),
            ("Lunch", "☀️", "#10B981"),
            ("Dinner", "🌙", "#8B5CF6"),
            ("Snack", "🍎", "#EF4444"),
            ("Dessert", "🍰", "#EC4899")
        ]
        
        for name, emoji, color in meal_types:
            await self.database.execute("""
                INSERT INTO meal_types (name, emoji, color)
                VALUES (:name, :emoji, :color)
            """, {"name": name, "emoji": emoji, "color": color})
        logger.info("✅ Meal types seeded")
        
        # Seed default categories for ideas
        logger.info("🔄 Seeding default categories...")
        categories = [
            ("Personal", "👤", "#10B981"),
            ("Work", "💼", "#3B82F6"),
            ("Health", "🏥", "#EF4444"),
            ("Learning", "📚", "#8B5CF6"),
            ("Travel", "✈️", "#F59E0B"),
            ("Technology", "💻", "#6B7280"),
            ("Creative", "🎨", "#EC4899"),
            ("Finance", "💰", "#84CC16")
        ]
        
        for name, emoji, color in categories:
            await self.database.execute("""
                INSERT INTO categories (name, emoji, color)
                VALUES (:name, :emoji, :color)
            """, {"name": name, "emoji": emoji, "color": color})
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
                    INSERT INTO users (email, username, hashed_password, is_active, is_superuser, role)
                    VALUES (:email, :username, :hashed_password, :is_active, :is_superuser, :role)
                """, {
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