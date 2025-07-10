#!/usr/bin/env python3
"""
Test script for database migration
"""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.migrate import main

if __name__ == "__main__":
    print("🧪 Testing database migration...")
    try:
        asyncio.run(main())
        print("✅ Migration test completed successfully!")
    except Exception as e:
        print(f"❌ Migration test failed: {e}")
        sys.exit(1)
    finally:
        # Clean up test database file
        if os.path.exists("test.db"):
            os.remove("test.db")
            print("🧹 Test database cleaned up") 