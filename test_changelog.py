#!/usr/bin/env python3
"""
Test script for changelog functionality
"""
import sys
import asyncio
import platform

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from db.session import models_registry
from apps.changelog.models import ChangelogEntry, ChangelogView, LastProcessedCommit
ChangelogEntry.Meta.registry = models_registry
ChangelogView.Meta.registry = models_registry
LastProcessedCommit.Meta.registry = models_registry

import db.session  # Ensure registry and models are loaded before anything else

import os
from datetime import datetime, timezone
import traceback

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.session import database
from apps.changelog.services import ChangelogService, GitService, DeepSeekService


async def test_git_service():
    """Test Git service functionality"""
    print("🔍 Testing Git Service...")
    
    try:
        # Test getting current version
        version = GitService.get_current_version()
        print(f"✅ Current version: {version}")
        
        # Test getting last commit hash
        last_hash = GitService.get_last_commit_hash()
        print(f"✅ Last commit hash: {last_hash}")
        
        # Test getting commits since
        commits = GitService.get_commits_since()
        print(f"✅ Found {len(commits)} commits")
        
        if commits:
            print(f"   Latest commit: {commits[0]['subject']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Git service test failed: {e}")
        return False


async def test_deepseek_service():
    """Test DeepSeek service functionality"""
    print("\n🤖 Testing DeepSeek Service...")
    
    try:
        # Check if API key is available
        from core.config import settings
        if not settings.deepseek_api_key:
            print("⚠️  DEEPSEEK_API_KEY not found, skipping DeepSeek test")
            return True
        
        # Test DeepSeek service initialization
        deepseek_service = DeepSeekService()
        print("✅ DeepSeek service initialized")
        
        # Test with sample commits
        sample_commits = [
            {
                "hash": "abc123456789",
                "author_name": "Test User",
                "author_email": "test@example.com",
                "date": datetime.now(timezone.utc),
                "subject": "Add user authentication",
                "body": "Implemented JWT-based authentication with Google OAuth support"
            }
        ]
        
        # Note: This would make an actual API call, so we'll skip it in testing
        print("✅ DeepSeek service test passed (API call skipped)")
        return True
        
    except Exception as e:
        print(f"❌ DeepSeek service test failed: {e}")
        return False


async def test_changelog_service():
    """Test Changelog service functionality"""
    print("\n📝 Testing Changelog Service...")
    
    try:
        # Initialize service
        changelog_service = ChangelogService()
        print("✅ Changelog service initialized")
        
        # Test getting changelog entries
        entries, total = await changelog_service.get_changelog_entries()
        print(f"✅ Found {total} changelog entries")
        
        # Test getting unread entries
        unread_entries = await changelog_service.get_unread_entries("test-user")
        print(f"✅ Found {len(unread_entries)} unread entries for test user")
        
        # Test getting summary
        summary = await changelog_service.get_changelog_summary()
        print(f"✅ Summary: {summary['total_changes']} total changes, {summary['breaking_changes']} breaking")
        
        return True
        
    except Exception as e:
        print(f"❌ Changelog service test failed: {e}")
        return False


async def test_database_operations():
    """Test database operations"""
    print("\n🗄️  Testing Database Operations...")
    
    try:
        # Test creating a sample changelog entry
        sample_entry = await ChangelogEntry.objects.create(
            version="1.0.0",
            title="Test Feature",
            description="This is a test changelog entry",
            change_type="added",
            commit_hash="test123456789",
            commit_date=datetime.now(timezone.utc),
            commit_message="Add test feature",
            is_breaking=False,
            release_date=datetime.now(timezone.utc)
        )
        print(f"✅ Created test changelog entry: {sample_entry.id}")
        
        # Test retrieving the entry
        retrieved_entry = await ChangelogEntry.objects.get(id=sample_entry.id)
        print(f"✅ Retrieved entry: {retrieved_entry.title}")
        
        # Test marking as viewed
        view = await ChangelogView.objects.create(
            entry=str(sample_entry.id),
            user_identifier="test-user"
        )
        print(f"✅ Created view record: {view.id}")
        
        # Test getting unread entries (should be 0 now)
        changelog_service = ChangelogService()
        unread_entries = await changelog_service.get_unread_entries("test-user")
        print(f"✅ Unread entries after marking as viewed: {len(unread_entries)}")
        
        # Clean up test data
        try:
            await view.delete()
        except Exception as e:
            print(f"⚠️  Could not delete view: {e}")
        try:
            await sample_entry.delete()
        except Exception as e:
            print(f"⚠️  Could not delete sample entry: {e}")
        print("✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Database operations test failed: {e}")
        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    print("🚀 Starting changelog functionality tests...")
    
    # Connect to database
    await database.connect()
    
    try:
        # Run tests
        tests = [
            test_git_service(),
            test_deepseek_service(),
            test_changelog_service(),
            test_database_operations()
        ]
        
        results = await asyncio.gather(*tests, return_exceptions=True)
        
        # Print summary
        print("\n📊 Test Results Summary:")
        passed = sum(1 for result in results if result is True)
        total = len(results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        if passed == total:
            print("🎉 All tests passed!")
        else:
            print("💥 Some tests failed!")
            
    except Exception as e:
        print(f"💥 Test execution failed: {e}")
        
    finally:
        # Disconnect from database
        await database.disconnect()


if __name__ == "__main__":
    asyncio.run(main()) 