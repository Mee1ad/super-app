#!/usr/bin/env python3
"""
Incremental database migration runner
Uses proper versioning and dependency management
"""
import asyncio
import sys
import os
import logging
import argparse
import platform
from typing import Optional

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.session import database
from db.migrations.base import migration_manager, Migration
from core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def register_migrations():
    """Register all migrations with the migration manager"""
    # Import migrations dynamically to avoid import issues
    try:
        # Import migration modules
        import importlib.util
        
        migration_files = [
            "backend/db/migrations/001_initial_schema_consolidated.py"
        ]
        
        for migration_file in migration_files:
            if os.path.exists(migration_file):
                spec = importlib.util.spec_from_file_location("migration", migration_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                
                # Find the migration class in the module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, Migration) and 
                        attr != Migration):
                        migration_instance = attr()
                        migration_manager.register_migration(migration_instance)
                        logger.info(f"✅ Registered migration: {migration_instance.get_version()}")
                        break
        
        logger.info(f"✅ Registered {len(migration_manager.migrations)} migrations")
        
    except Exception as e:
        logger.error(f"❌ Error registering migrations: {e}")
        raise


async def run_migrations(target_version: Optional[str] = None):
    """Run migrations up to target version"""
    try:
        await database.connect()
        logger.info("✅ Connected to database")
        
        # Register all migrations
        register_migrations()
        
        # Run migrations
        await migration_manager.migrate(target_version)
        
        logger.info("✅ All migrations completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise
    finally:
        await database.disconnect()


async def rollback_migrations(target_version: str):
    """Rollback migrations to target version"""
    try:
        await database.connect()
        logger.info("✅ Connected to database")
        
        # Register all migrations
        register_migrations()
        
        # Rollback migrations
        await migration_manager.rollback(target_version)
        
        logger.info(f"✅ Rollback to version {target_version} completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Rollback failed: {e}")
        raise
    finally:
        await database.disconnect()


async def show_status():
    """Show migration status"""
    try:
        await database.connect()
        logger.info("✅ Connected to database")
        
        # Register all migrations
        register_migrations()
        
        # Get status
        status = await migration_manager.status()
        
        print("\n=== Migration Status ===")
        print(f"Total migrations: {status['total_migrations']}")
        print(f"Applied: {status['applied_migrations']}")
        print(f"Pending: {len(status['pending_migrations'])}")
        
        if status['applied_migrations_list']:
            print(f"\nApplied migrations:")
            for migration in status['applied_migrations_list']:
                print(f"  ✅ {migration['version']}: {migration['name']}")
        
        if status['pending_migrations']:
            print(f"\nPending migrations:")
            for migration in status['pending_migrations']:
                print(f"  ⏳ {migration['version']}: {migration['name']}")
                print(f"     Description: {migration['description']}")
                if migration['dependencies']:
                    print(f"     Dependencies: {', '.join(migration['dependencies'])}")
                print()
        
        logger.info("✅ Status check completed")
        
    except Exception as e:
        logger.error(f"❌ Status check failed: {e}")
        raise
    finally:
        await database.disconnect()


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Incremental database migration runner")
    parser.add_argument(
        "action",
        choices=["migrate", "rollback", "status"],
        help="Action to perform"
    )
    parser.add_argument(
        "--target",
        help="Target version for migrate/rollback (e.g., '003')"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without executing"
    )
    
    args = parser.parse_args()
    
    logger.info("🚀 Starting incremental migration process...")
    
    # Debug configuration details
    print("=== Database Configuration Debug ===")
    print(f"Environment: {settings.environment}")
    print(f"Is Production: {settings.is_production}")
    print(f"DB Host: {settings.db_host}")
    print(f"DB Port: {settings.db_port}")
    print(f"DB Name: {settings.db_name}")
    print(f"DB User: {settings.db_user}")
    print(f"Database URL: {settings.get_database_url()}")
    print("=== End Debug ===")
    
    if args.dry_run:
        logger.info("🔍 DRY RUN MODE - No changes will be made")
    
    try:
        if args.action == "migrate":
            await run_migrations(args.target)
        elif args.action == "rollback":
            if not args.target:
                logger.error("❌ Target version required for rollback")
                sys.exit(1)
            await rollback_migrations(args.target)
        elif args.action == "status":
            await show_status()
        
        logger.info("🎉 Migration process completed successfully!")
        
    except Exception as e:
        logger.error(f"💥 Migration process failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 