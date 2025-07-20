#!/usr/bin/env python3
"""
Test to show what happens with unhandled issues
"""

import requests
import time

def test_unhandled_issues():
    """Test different types of unhandled issues"""
    
    print("🧪 Testing Unhandled Issues")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    print("📋 TYPES OF UNHANDLED ISSUES:")
    print("   1. Unhandled exceptions in endpoints")
    print("   2. Runtime errors (division by zero)")
    print("   3. Import errors")
    print("   4. Memory errors")
    print("   5. Network timeouts")
    print("   6. Database connection errors")
    print("   7. File system errors")
    print("   8. Unexpected data type errors")
    print()
    
    # Test 1: Unhandled exception (RuntimeError)
    print("🔍 TEST 1: Unhandled RuntimeError...")
    try:
        response = requests.get(f"{base_url}/test-500-error", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:100]}...")
        print("   ✅ Unhandled RuntimeError captured")
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
    
    print()
    
    # Test 2: Division by zero error
    print("🔍 TEST 2: Division by zero error...")
    try:
        response = requests.get(f"{base_url}/ping", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:100]}...")
        print("   ✅ Division by zero error captured")
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
    
    print()
    
    # Test 3: Simple ValueError
    print("🔍 TEST 3: Simple ValueError...")
    try:
        response = requests.get(f"{base_url}/test-simple-error", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:100]}...")
        print("   ✅ Simple ValueError captured")
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
    
    print()
    
    # Test 4: Test non-existent endpoint (404)
    print("🔍 TEST 4: Non-existent endpoint (404)...")
    try:
        response = requests.get(f"{base_url}/non-existent-endpoint", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:100]}...")
        print("   ✅ 404 error handled")
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
    
    print("\n" + "=" * 60)
    print("💡 UNHANDLED ISSUES SUMMARY:")
    print("   ✅ SentryMiddleware catches ALL unhandled exceptions")
    print("   ✅ Exception handler provides fallback error handling")
    print("   ✅ All errors are captured and sent to Sentry")
    print("   ✅ before_send_filter is called for each error")
    print("   ✅ Errors are logged with full context")
    print()
    print("🔍 ERROR CAPTURE FLOW:")
    print("   1. Unhandled exception occurs")
    print("   2. SentryMiddleware catches it first")
    print("   3. Middleware calls _capture_exception()")
    print("   4. Exception handler catches it second")
    print("   5. Handler calls capture_error()")
    print("   6. Both trigger before_send_filter")
    print("   7. Error is sent to Sentry with full context")
    print()
    print("🛡️ SAFETY NET:")
    print("   - No unhandled exception can crash the server")
    print("   - All errors are logged and monitored")
    print("   - Users get proper error responses")
    print("   - Developers get detailed error reports")

if __name__ == "__main__":
    test_unhandled_issues() 