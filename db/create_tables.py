#!/usr/bin/env python3
"""
Script to create database tables for the super-app-backend using Edgy Registry
"""
import asyncio
import sys
import os

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.session import models_registry, database
from core.config import settings

async def create_tables():
    """Create all database tables"""
    try:
        print(f"Connecting to database: {settings.database_url}")
        await database.connect()
        print("✅ Database connection successful.")
        print(f"Registered models in registry: {list(models_registry.models.keys())}")
        await models_registry.create_all()
        print("✅ Database tables created successfully!")
        tables = models_registry.get_tablenames()
        print(f"📋 Registry tables: {', '.join(tables)}")
        # List tables from the actual database
        result = await database.fetch_all("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        print("📋 Tables in DB:", [row[0] for row in result])
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await database.disconnect()


if __name__ == "__main__":
    asyncio.run(create_tables()) 