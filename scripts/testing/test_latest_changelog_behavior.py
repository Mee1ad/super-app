#!/usr/bin/env python3
"""
Test script to verify the new latest changelog behavior.
This script tests that the /latest endpoint checks if hashed data exists first.
"""

import asyncio
import sys
import os
import platform

# Fix Windows event loop issue
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from apps.changelog.services import ChangelogService
from apps.changelog.models import ChangelogEntry, ChangelogView, ChangeType
from datetime import datetime, timezone
import apps.auth.models  # Ensure User model is registered with Edgy ORM
from apps.auth.models import User

async def create_test_user():
    """Create a test user for publishing changelog entries"""
    print("📝 Creating test user...")
    user = await User.objects.create(
        email="test_changelog_user@example.com",
        username="test_changelog_user",
        hashed_password="testpassword",
        is_active=True,
        is_superuser=False
    )
    print(f"   Created test user: {user.email}")
    return user

async def cleanup_test_user(user):
    if user:
        await user.delete()
        print("   Deleted test user")

async def create_sample_changelog_data(test_user):
    """Create sample changelog data for testing"""
    print("📝 Creating sample changelog data...")
    sample_entry = await ChangelogEntry.objects.create(
        version="1.2.0",
        title="Test Feature",
        description="This is a test changelog entry",
        change_type=ChangeType.ADDED,
        is_breaking=False,
        commit_hash="abc123",
        commit_date=datetime.now(timezone.utc),
        commit_message="Add test feature",
        release_date=datetime.now(timezone.utc),
        is_published=True,
        published_by=test_user,
        published_at=datetime.now(timezone.utc)
    )
    print(f"   Created sample entry: {sample_entry.title} (v{sample_entry.version})")
    return sample_entry

async def cleanup_sample_data(sample_entry):
    if sample_entry:
        await sample_entry.delete()
        print("   Deleted sample changelog entry")


async def test_latest_changelog_behavior():
    """Test the new latest changelog behavior"""
    print("🧪 Testing Latest Changelog Behavior")
    print("=" * 50)
    
    service = ChangelogService()
    
    # Test data
    test_ip = "192.168.1.100"
    test_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    print(f"📝 Test IP: {test_ip}")
    print(f"📝 Test User-Agent: {test_user_agent[:50]}...")
    print()
    
    # Step 1: Test with no existing hash data (should show changelog)
    print("1️⃣ Testing with no existing hash data...")
    result1 = await service.get_latest_changelog_for_user(test_ip, test_user_agent)
    
    print(f"   Result: {result1['reason']}")
    print(f"   Has entries: {len(result1['entries']) > 0}")
    print(f"   Has new content: {result1['has_new_content']}")
    print()
    
    # Step 2: Mark as viewed (creates hash data)
    print("2️⃣ Marking as viewed (creates hash data)...")
    success = await service.mark_as_viewed(test_ip, test_user_agent)
    print(f"   Success: {success}")
    print()
    
    # Step 3: Test with existing hash data (should return empty)
    print("3️⃣ Testing with existing hash data...")
    result2 = await service.get_latest_changelog_for_user(test_ip, test_user_agent)
    
    print(f"   Result: {result2['reason']}")
    print(f"   Has entries: {len(result2['entries']) > 0}")
    print(f"   Has new content: {result2['has_new_content']}")
    print()
    
    # Step 4: Debug user views
    print("4️⃣ Debug user views...")
    debug_info = await service.debug_user_views(test_ip, test_user_agent)
    print(f"   Total views: {debug_info['total_views']}")
    if debug_info['views']:
        view = debug_info['views'][0]
        print(f"   Latest version seen: {view['latest_version_seen']}")
        print(f"   View count: {view['view_count']}")
    print()
    
    # Summary
    print("📊 Summary:")
    print(f"   First call (no hash): {result1['reason']} - Entries: {len(result1['entries'])}")
    print(f"   Second call (with hash): {result2['reason']} - Entries: {len(result2['entries'])}")
    
    # Verify the behavior
    if result1['reason'] == 'new_user' and result2['reason'] == 'user_already_seen':
        print("✅ Test PASSED: Hash data check works correctly!")
        return True
    else:
        print("❌ Test FAILED: Unexpected behavior!")
        return False


async def cleanup_test_data():
    """Clean up any test data created"""
    print("\n🧹 Cleaning up test data...")
    
    # Remove test views
    test_ip = "192.168.1.100"
    test_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    service = ChangelogService()
    hashed_ip = service._hash_ip_address(test_ip)
    hashed_user_agent = service._hash_user_agent(test_user_agent)
    
    # Delete test views
    views = await ChangelogView.objects.filter(
        hashed_ip=hashed_ip,
        hashed_user_agent=hashed_user_agent
    ).all()
    
    for view in views:
        await view.delete()
    
    print(f"   Deleted {len(views)} test view records")


if __name__ == "__main__":
    print("🚀 Starting Latest Changelog Behavior Test")
    print("=" * 60)
    
    try:
        # Create test user
        test_user = asyncio.run(create_test_user())
        # Create sample data
        sample_entry = asyncio.run(create_sample_changelog_data(test_user))
        # Run the test
        success = asyncio.run(test_latest_changelog_behavior())
        # Clean up
        asyncio.run(cleanup_test_data())
        asyncio.run(cleanup_sample_data(sample_entry))
        asyncio.run(cleanup_test_user(test_user))
        if success:
            print("\n🎉 All tests completed successfully!")
            sys.exit(0)
        else:
            print("\n💥 Tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        sys.exit(1) 