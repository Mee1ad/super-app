#!/usr/bin/env python3
"""
Simple test to verify changelog service methods are working correctly.
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


async def test_service_methods():
    """Test the changelog service methods"""
    print("🧪 Testing Changelog Service Methods")
    print("=" * 45)
    
    service = ChangelogService()
    
    # Test data
    test_ip = "192.168.1.200"
    test_user_agent = "Mozilla/5.0 (Test Browser) AppleWebKit/537.36"
    
    print(f"📝 Test IP: {test_ip}")
    print(f"📝 Test User-Agent: {test_user_agent}")
    print()
    
    # Test 1: Get latest changelog (should show entries for new user)
    print("1️⃣ Testing GET /changelog/latest (new user)...")
    try:
        result = await service.get_latest_changelog_for_user(
            ip_address=test_ip,
            user_agent=test_user_agent,
            limit=5
        )
        print(f"   ✅ Success: {result['total']} entries, reason: {result['reason']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 2: Mark as viewed
    print("2️⃣ Testing POST /changelog/viewed...")
    try:
        success = await service.mark_as_viewed(
            ip_address=test_ip,
            user_agent=test_user_agent
        )
        print(f"   ✅ Success: {success}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 3: Get latest changelog again (should return empty)
    print("3️⃣ Testing GET /changelog/latest (after viewed)...")
    try:
        result = await service.get_latest_changelog_for_user(
            ip_address=test_ip,
            user_agent=test_user_agent,
            limit=5
        )
        print(f"   ✅ Success: {result['total']} entries, reason: {result['reason']}")
        
        if result['total'] == 0 and result['reason'] == "user_already_seen":
            print("   🎉 Perfect! User has seen changelog, no entries returned.")
        else:
            print("   ⚠️  Unexpected result - user should have seen changelog.")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 4: Debug user views
    print("4️⃣ Testing GET /changelog/debug...")
    try:
        debug_info = await service.debug_user_views(
            ip_address=test_ip,
            user_agent=test_user_agent
        )
        print(f"   ✅ Success: {debug_info['total_views']} views found")
        if debug_info['views']:
            view = debug_info['views'][0]
            print(f"   📊 Latest version seen: {view['latest_version_seen']}")
            print(f"   📊 View count: {view['view_count']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n✅ Service method tests completed!")


if __name__ == "__main__":
    print("🚀 Starting Service Method Tests")
    print("=" * 55)
    
    try:
        asyncio.run(test_service_methods())
        print("\n🎉 All service method tests completed!")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        sys.exit(1) 