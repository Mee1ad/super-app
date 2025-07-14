"""
Database migration for changelog tables
"""
import asyncio
import sys
import os
import platform

# Set event loop policy for Windows compatibility
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.session import database, models_registry

async def create_changelog_tables():
    """Create changelog tables in the database"""
    try:
        # Create tables using the registry
        await models_registry.create_all()
        print("✅ Changelog tables created successfully")
    except Exception as e:
        print(f"❌ Error creating changelog tables: {e}")
        raise

async def main():
    """Main migration function"""
    print("🚀 Starting changelog migration...")
    await database.connect()
    try:
        await create_changelog_tables()
        print("🎉 Changelog migration completed successfully!")
    except Exception as e:
        print(f"💥 Migration failed: {e}")
        raise
    finally:
        await database.disconnect()

if __name__ == "__main__":
    asyncio.run(main()) 