#!/usr/bin/env python3
"""
Test script for the new incremental migration system
"""
import asyncio
import sys
import os
import platform

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.migrate_incremental import main

async def test_migration_system():
    """Test the migration system"""
    print("🧪 Testing Incremental Migration System")
    print("=" * 50)
    
    # Test 1: Show status
    print("\n1. Checking migration status...")
    sys.argv = ["migrate_incremental.py", "status"]
    await main()
    
    # Test 2: Run migrations
    print("\n2. Running migrations...")
    sys.argv = ["migrate_incremental.py", "migrate"]
    await main()
    
    # Test 3: Show status again
    print("\n3. Checking migration status after running...")
    sys.argv = ["migrate_incremental.py", "status"]
    await main()
    
    print("\n✅ Migration system test completed!")

if __name__ == "__main__":
    asyncio.run(test_migration_system()) 