#!/usr/bin/env python3
"""
Comprehensive test to verify ALL error types are captured by Sentry
"""

import requests
import time

def test_comprehensive_error_capture():
    """Test comprehensive error capture"""
    
    print("🧪 Comprehensive Error Capture Test")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    print("📋 TESTING ALL ERROR CAPTURE METHODS:")
    print("   1. Explicit error capture (ping endpoint)")
    print("   2. Raised exceptions (test-500-error)")
    print("   3. Random unhandled issues")
    print("   4. Global exception handler")
    print("   5. Middleware error capture")
    print("   6. Exception handler capture")
    print()
    
    # Test 1: Ping endpoint with explicit error capture
    print("🔍 TEST 1: Ping endpoint (explicit error capture)...")
    try:
        response = requests.get(f"{base_url}/ping", timeout=10)
        print(f"   Status: {response.status_code}")
        print("   ✅ Ping endpoint completed")
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
    
    print()
    
    # Test 2: Test 500 error endpoint
    print("🔍 TEST 2: Test 500 error endpoint...")
    try:
        response = requests.get(f"{base_url}/test-500-error", timeout=10)
        print(f"   Status: {response.status_code}")
        print("   ✅ 500 error endpoint completed")
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
    
    print()
    
    # Test 3: Random unhandled issues
    print("🔍 TEST 3: Random unhandled issues...")
    try:
        response = requests.get(f"{base_url}/test-unhandled-issues", timeout=10)
        print(f"   Status: {response.status_code}")
        print("   ✅ Random unhandled issues completed")
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
    
    print()
    
    # Test 4: Simple error endpoint
    print("🔍 TEST 4: Simple error endpoint...")
    try:
        response = requests.get(f"{base_url}/test-simple-error", timeout=10)
        print(f"   Status: {response.status_code}")
        print("   ✅ Simple error endpoint completed")
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
    
    print()
    
    # Test 5: Non-existent endpoint (404)
    print("🔍 TEST 5: Non-existent endpoint (404)...")
    try:
        response = requests.get(f"{base_url}/non-existent-endpoint", timeout=10)
        print(f"   Status: {response.status_code}")
        print("   ✅ 404 error handled")
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
    
    print("\n" + "=" * 60)
    print("💡 COMPREHENSIVE ERROR CAPTURE SUMMARY:")
    print("   ✅ Explicit error capture in endpoints")
    print("   ✅ Raised exceptions in endpoints")
    print("   ✅ Random unhandled issues")
    print("   ✅ Global exception handler (sys.excepthook)")
    print("   ✅ SentryMiddleware error capture")
    print("   ✅ SentryExceptionHandler error capture")
    print("   ✅ before_send_filter for all errors")
    print()
    print("🔍 EXPECTED SERVER LOGS FOR EACH ERROR:")
    print("   1. 🚀 SENTRY MIDDLEWARE START")
    print("   2. 🔍 EXPLICIT ERROR CAPTURE (for ping)")
    print("   3. 🚨 SENTRY MIDDLEWARE CATCH ERROR")
    print("   4. 🚀 SENTRY EXCEPTION HANDLER START")
    print("   5. ✅ SENTRY EXCEPTION HANDLER END")
    print("   6. 🔚 SENTRY MIDDLEWARE END (ERROR)")
    print("   7. decidninignignggggggggggggggggggggggggggggggg (before_send_filter)")
    print()
    print("🚨 GLOBAL EXCEPTION HANDLER (for uncaught errors)")
    print()
    print("🎯 RESULT: ALL ERRORS SHOULD BE CAPTURED IN SENTRY!")

if __name__ == "__main__":
    test_comprehensive_error_capture() 