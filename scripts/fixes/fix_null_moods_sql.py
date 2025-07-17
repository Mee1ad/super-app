#!/usr/bin/env python3
import sys
import os
import asyncio
from pathlib import Path

# Fix for Windows event loop
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from db.session import database

DEFAULT_EMOJI = "🙂"
DEFAULT_COLOR = "#CCCCCC"

async def fix_null_moods_sql():
    try:
        await database.connect()
        # Update emoji where null
        result1 = await database.execute(
            f"""
            UPDATE moods SET emoji = '{DEFAULT_EMOJI}' WHERE emoji IS NULL;
            """
        )
        # Update color where null
        result2 = await database.execute(
            f"""
            UPDATE moods SET color = '{DEFAULT_COLOR}' WHERE color IS NULL;
            """
        )
        print("Updated moods with missing emoji or color using raw SQL.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.disconnect()

if __name__ == "__main__":
    asyncio.run(fix_null_moods_sql()) 