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

async def check_moods_data():
    """Check the moods data in the database"""
    try:
        # Connect to database
        await database.connect()
        
        # Get all moods
        moods = await Mood.objects.all()
        
        print(f"Found {len(moods)} moods:")
        print("-" * 50)
        
        for mood in moods:
            print(f"ID: {mood.id} (type: {type(mood.id)})")
            print(f"Name: {mood.name}")
            print(f"Emoji: {mood.emoji}")
            print(f"Color: {mood.color}")
            print(f"Created at: {mood.created_at}")
            print("-" * 30)
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.disconnect()

if __name__ == "__main__":
    asyncio.run(check_moods_data()) 