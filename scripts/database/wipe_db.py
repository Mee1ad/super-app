#!/usr/bin/env python3
"""
Wipe the entire database by dropping and recreating the public schema.
"""
import asyncio
import sys
import os
import platform

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from db.session import database

async def wipe_db():
    try:
        await database.connect()
        print("🗑️  Dropping public schema...")
        await database.execute("DROP SCHEMA public CASCADE")
        print("📝 Recreating public schema...")
        await database.execute("CREATE SCHEMA public")
        print("✅ Database wiped successfully!")
    except Exception as e:
        print(f"❌ Error wiping database: {e}")
        raise
    finally:
        await database.disconnect()

if __name__ == "__main__":
    asyncio.run(wipe_db()) 