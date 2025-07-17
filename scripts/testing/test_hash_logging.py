#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced hash logging in /changelog/latest endpoint.
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

import apps.auth.models  # Ensure User model is registered with Edgy ORM
from apps.auth.models import User
from apps.changelog.services import ChangelogService
from apps.changelog.models import ChangelogEntry, ChangelogView, ChangeType
from datetime import datetime, timezone


async def create_test_data():
    """Create test user and changelog entry"""
    print("📝 Creating test data...")
    
    # Create test user
    user = await User.objects.create(
        email="test_hash_user@example.com",
        username="test_hash_user",
        hashed_password="testpassword",
        is_active=True,
        is_superuser=False
    )
    
    # Create test changelog entry
    entry = await ChangelogEntry.objects.create(
        version="1.3.0",
        title="Enhanced Hash Logging",
        description="Added detailed logging to show hash values",
        change_type=ChangeType.ADDED,
        is_breaking=False,
        commit_hash="hash123",
        commit_date=datetime.now(timezone.utc),
        commit_message="Add hash logging",
        release_date=datetime.now(timezone.utc),
        is_published=True,
        published_by=user,
        published_at=datetime.now(timezone.utc)
    )
    
    print(f"   ✅ Created test user: {user.email}")
    print(f"   ✅ Created changelog entry: {entry.title} (v{entry.version})")
    return user, entry


async def cleanup_test_data(user, entry):
    """Clean up test data"""
    if entry:
        await entry.delete()
        print("   🗑️  Deleted test changelog entry")
    if user:
        await user.delete()
        print("   🗑️  Deleted test user")


async def test_hash_logging():
    """Test the enhanced hash logging"""
    print("🧪 Testing Enhanced Hash Logging")
    print("=" * 50)
    
    service = ChangelogService()
    
    # Test data
    test_ip = "192.168.1.300"
    test_user_agent = "Mozilla/5.0 (Test Browser) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    print(f"📝 Test IP: {test_ip}")
    print(f"📝 Test User-Agent: {test_user_agent}")
    print()
    
    # Test 1: First request (should show changelog)
    print("1️⃣ First request to /changelog/latest (new user)...")
    print("   (This should show detailed hash logging)")
    print()
    
    result1 = await service.get_latest_changelog_for_user(
        ip_address=test_ip,
        user_agent=test_user_agent,
        limit=5
    )
    
    print(f"   Result: {result1['reason']} - {result1['total']} entries")
    print()
    
    # Test 2: Mark as viewed
    print("2️⃣ Marking as viewed...")
    print("   (This should show detailed hash logging)")
    print()
    
    success = await service.mark_as_viewed(
        ip_address=test_ip,
        user_agent=test_user_agent
    )
    
    print(f"   Success: {success}")
    print()
    
    # Test 3: Second request (should return empty)
    print("3️⃣ Second request to /changelog/latest (after viewed)...")
    print("   (This should show detailed hash logging)")
    print()
    
    result2 = await service.get_latest_changelog_for_user(
        ip_address=test_ip,
        user_agent=test_user_agent,
        limit=5
    )
    
    print(f"   Result: {result2['reason']} - {result2['total']} entries")
    
    if result2['total'] == 0 and result2['reason'] == "user_already_seen":
        print("   🎉 Perfect! Hash tracking is working correctly!")
    else:
        print("   ⚠️  Unexpected result!")
    
    print()
    
    # Test 4: Debug endpoint
    print("4️⃣ Debug endpoint to see stored data...")
    debug_info = await service.debug_user_views(
        ip_address=test_ip,
        user_agent=test_user_agent
    )
    
    print(f"   Total views: {debug_info['total_views']}")
    if debug_info['views']:
        view = debug_info['views'][0]
        print(f"   Latest version seen: {view['latest_version_seen']}")
        print(f"   View count: {view['view_count']}")
    
    print("\n✅ Hash logging test completed!")


if __name__ == "__main__":
    print("🚀 Starting Enhanced Hash Logging Test")
    print("=" * 60)
    
    try:
        # Create test data
        user, entry = asyncio.run(create_test_data())
        
        # Run the test
        asyncio.run(test_hash_logging())
        
        # Clean up
        asyncio.run(cleanup_test_data(user, entry))
        
        print("\n🎉 All tests completed successfully!")
        print("\n📋 The logs above show the full hash values being used!")
        
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        sys.exit(1) 