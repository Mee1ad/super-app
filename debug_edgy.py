#!/usr/bin/env python3
"""
Debug script to test Edgy ORM model registration
"""
import sys
import os
import asyncio

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🔍 Testing Edgy ORM Model Registration...")

# Test 1: Import registry and check if it exists
try:
    from db.session import models_registry, database
    print("✅ models_registry imported successfully")
    print(f"   Registry database: {models_registry.database}")
except Exception as e:
    print(f"❌ Failed to import models_registry: {e}")
    sys.exit(1)

# Test 2: Import working model (User) and check objects
try:
    from apps.auth.models import User
    print("✅ User model imported successfully")
    print(f"   User has objects: {hasattr(User, 'objects')}")
    print(f"   User Meta registry: {User.Meta.registry}")
    print(f"   User in registry: {User.__name__ in models_registry.models}")
except Exception as e:
    print(f"❌ Failed to import User model: {e}")

# Test 3: Import changelog models and check objects
try:
    from apps.changelog.models import ChangelogEntry, ChangelogView, LastProcessedCommit
    print("✅ Changelog models imported successfully")
    
    for model_name, model in [("ChangelogEntry", ChangelogEntry), 
                             ("ChangelogView", ChangelogView), 
                             ("LastProcessedCommit", LastProcessedCommit)]:
        print(f"   {model_name}:")
        print(f"     Has objects: {hasattr(model, 'objects')}")
        print(f"     Meta registry: {model.Meta.registry}")
        print(f"     In registry: {model.__name__ in models_registry.models}")
        
except Exception as e:
    print(f"❌ Failed to import changelog models: {e}")

# Test 4: Check all registered models
print(f"\n📋 All registered models: {list(models_registry.models.keys())}")

# Test 5: Connect to database and check if objects become available
async def test_with_database():
    print("\n🔌 Testing with database connection...")
    try:
        await database.connect()
        print("✅ Database connected successfully")
        
        # Check if objects are now available
        print(f"   User has objects: {hasattr(User, 'objects')}")
        print(f"   ChangelogEntry has objects: {hasattr(ChangelogEntry, 'objects')}")
        
        # Try to use objects
        if hasattr(User, 'objects'):
            print("   ✅ User.objects is available!")
        if hasattr(ChangelogEntry, 'objects'):
            print("   ✅ ChangelogEntry.objects is available!")
            
        await database.disconnect()
        print("✅ Database disconnected")
        
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")

# Run the async test
asyncio.run(test_with_database())

print("\n🎯 Debug complete!") 