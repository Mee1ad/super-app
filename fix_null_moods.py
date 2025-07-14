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
from apps.diary.models import Mood

DEFAULT_EMOJI = "🙂"
DEFAULT_COLOR = "#CCCCCC"

async def fix_null_moods():
    try:
        await database.connect()
        moods = await Mood.objects.all()
        updated = 0
        for mood in moods:
            needs_update = False
            if not mood.emoji:
                mood.emoji = DEFAULT_EMOJI
                needs_update = True
            if not mood.color:
                mood.color = DEFAULT_COLOR
                needs_update = True
            if needs_update:
                await mood.save()
                updated += 1
        print(f"Updated {updated} moods with missing emoji or color.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.disconnect()

if __name__ == "__main__":
    asyncio.run(fix_null_moods()) 