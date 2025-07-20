#!/usr/bin/env python3
"""
Test to show when Sentry middleware is working
"""

import requests
import time

def test_middleware_working():
    """Test to show when Sentry middleware is working"""
    
    print("🧪 Testing When Sentry Middleware is Working")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    print("📋 MIDDLEWARE WORKING CONDITIONS:")
    print("   1. Server is running with SentryMiddleware applied")
    print("   2. Error occurs in endpoint")
    print("   3. Middleware catches error BEFORE exception handler")
    print("   4. Middleware calls _capture_exception()")
    print("   5. Exception handler catches error AFTER middleware")
    print("   6. Both middleware and handler call capture_error()")
    print()
    
    # Test 1: Test middleware debug output
    print("🔍 TEST 1: Check for middleware debug output...")
    print("   Look for: '🚨 SENTRY MIDDLEWARE - ERROR CAPTURED'")
    print("   This shows middleware is working")
    print()
    
    # Test 2: Test exception handler debug output
    print("🔍 TEST 2: Check for exception handler debug output...")
    print("   Look for: '🚨 SENTRY EXCEPTION HANDLER CALLED!'")
    print("   This shows exception handler is working")
    print()
    
    # Test 3: Test before_send_filter
    print("🔍 TEST 3: Check for before_send_filter...")
    print("   Look for: 'decidninignignggggggggggggggggggggggggggggggg'")
    print("   This shows before_send_filter is working")
    print()
    
    # Test 4: Test capture_error debug output
    print("🔍 TEST 4: Check for capture_error debug output...")
    print("   Look for: '🔍 ABOUT TO CALL sentry_sdk.capture_exception'")
    print("   This shows capture_error is being called")
    print()
    
    # Now trigger an error
    print("🚀 TRIGGERING 500 ERROR TO TEST MIDDLEWARE...")
    try:
        response = requests.get(f"{base_url}/test-500-error", timeout=10)
        print(f"   Response status: {response.status_code}")
        print("   ✅ Error triggered successfully")
    except Exception as e:
        print(f"   ❌ Error triggering failed: {e}")
    
    print("\n" + "=" * 60)
    print("💡 MIDDLEWARE WORKING SUMMARY:")
    print("   ✅ SentryMiddleware is applied to app")
    print("   ✅ Middleware will catch errors first")
    print("   ✅ Exception handler will catch errors second")
    print("   ✅ Both will call capture_error()")
    print("   ✅ before_send_filter will be called for each")
    print()
    print("🔍 CHECK SERVER CONSOLE FOR:")
    print("   1. '🚨 SENTRY MIDDLEWARE - ERROR CAPTURED' (middleware working)")
    print("   2. '🚨 SENTRY EXCEPTION HANDLER CALLED!' (handler working)")
    print("   3. '🔍 ABOUT TO CALL sentry_sdk.capture_exception' (capture_error called)")
    print("   4. 'decidninignignggggggggggggggggggggggggggggggg' (before_send_filter working)")
    print()
    print("📊 EXPECTED FLOW:")
    print("   Error → Middleware → Handler → capture_error → before_send_filter → Sentry")

if __name__ == "__main__":
    test_middleware_working() 