#!/usr/bin/env python3
"""
Comprehensive database integration test
Validates schema, models, and API functionality
"""
import sys
import asyncio
import platform
import traceback

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db.session import database, models_registry
from apps.auth.models import User, Role
from apps.changelog.models import ChangelogEntry, ChangelogView, LastProcessedCommit

async def test_database_connection():
    """Test database connection"""
    print("🔌 Testing database connection...")
    try:
        # Test connection
        await database.connect()
        print("✅ Database connected successfully")
        
        # Test query
        result = await database.fetch_one("SELECT 1 as test")
        if result:
            print("✅ Database query test passed")
        else:
            print("❌ Database query test failed")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def test_table_schema():
    """Test if all required tables and columns exist"""
    print("\n📋 Testing table schema...")
    
    required_tables = {
        'users': ['id', 'email', 'username', 'hashed_password', 'is_active', 'is_superuser', 'role_id', 'created_at', 'updated_at'],
        'roles': ['id', 'name', 'description', 'permissions', 'created_at', 'updated_at'],
        'changelog_entries': ['id', 'version', 'title', 'description', 'change_type', 'commit_hash', 'commit_date', 'commit_message', 'is_breaking', 'release_date', 'is_published', 'published_by', 'published_at', 'created_at', 'updated_at'],
        'changelog_views': ['id', 'entry', 'user_identifier', 'viewed_at', 'created_at', 'updated_at'],
        'last_processed_commits': ['id', 'commit_hash', 'processed_at', 'created_at', 'updated_at']
    }
    
    all_passed = True
    
    for table_name, required_columns in required_tables.items():
        try:
            # Check if table exists
            result = await database.fetch_one(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = :table_name)",
                {"table_name": table_name}
            )
            
            if not result or not result[0]:
                print(f"❌ Table '{table_name}' does not exist")
                all_passed = False
                continue
                
            print(f"✅ Table '{table_name}' exists")
            
            # Check columns
            for column in required_columns:
                result = await database.fetch_one(
                    "SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = :table_name AND column_name = :column_name)",
                    {"table_name": table_name, "column_name": column}
                )
                
                if not result or not result[0]:
                    print(f"❌ Column '{column}' missing from table '{table_name}'")
                    all_passed = False
                else:
                    print(f"  ✅ Column '{column}' exists")
                    
        except Exception as e:
            print(f"❌ Error checking table '{table_name}': {e}")
            all_passed = False
    
    return all_passed

async def test_model_operations():
    """Test model operations"""
    print("\n🏗️  Testing model operations...")
    
    try:
        # Test User model
        print("Testing User model...")
        
        # Check if we can query users
        users = await User.objects.all()
        print(f"✅ User query successful, found {len(users)} users")
        
        # Test Role model
        print("Testing Role model...")
        roles = await Role.objects.all()
        print(f"✅ Role query successful, found {len(roles)} roles")
        
        # Test ChangelogEntry model
        print("Testing ChangelogEntry model...")
        entries = await ChangelogEntry.objects.all()
        print(f"✅ ChangelogEntry query successful, found {len(entries)} entries")
        
        return True
        
    except Exception as e:
        print(f"❌ Model operations failed: {e}")
        traceback.print_exc()
        return False

async def test_auth_service():
    """Test authentication service"""
    print("\n🔐 Testing authentication service...")
    
    try:
        from apps.auth.services import get_or_create_user_from_google
        
        # Test with mock Google user info
        mock_google_user = {
            "email": "test@example.com",
            "sub": "test_google_id",
            "name": "Test User"
        }
        
        # This should not fail due to database schema issues
        user = await get_or_create_user_from_google(mock_google_user)
        print(f"✅ Auth service test passed, user: {user.email}")
        
        return True
        
    except Exception as e:
        print(f"❌ Auth service test failed: {e}")
        traceback.print_exc()
        return False

async def test_changelog_service():
    """Test changelog service"""
    print("\n📝 Testing changelog service...")
    
    try:
        from apps.changelog.services import ChangelogService
        
        service = ChangelogService()
        
        # Test getting changelog entries
        entries, total = await service.get_changelog_entries()
        print(f"✅ Changelog service test passed, found {total} entries")
        
        return True
        
    except Exception as e:
        print(f"❌ Changelog service test failed: {e}")
        traceback.print_exc()
        return False

async def run_all_tests():
    """Run all integration tests"""
    print("🚀 Starting comprehensive database integration tests...\n")
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Table Schema", test_table_schema),
        ("Model Operations", test_model_operations),
        ("Auth Service", test_auth_service),
        ("Changelog Service", test_changelog_service)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results Summary:")
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Database integration is working correctly.")
        return True
    else:
        print("💥 Some tests failed! Please fix the issues before deployment.")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1) 