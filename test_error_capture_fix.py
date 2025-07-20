#!/usr/bin/env python3
"""
Test to verify error capture is working properly
"""

import requests
import time

def test_error_capture_fix():
    """Test error capture with the new changes"""
    
    print("🧪 Testing Error Capture Fix")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    print("📋 TESTING DIFFERENT ERROR TYPES:")
    print("   1. Explicit error capture (ping endpoint)")
    print("   2. Raised exception (test-500-error)")
    print("   3. Random unhandled issues")
    print()
    
    # Test 1: Ping endpoint with explicit error capture
    print("🔍 TEST 1: Ping endpoint (explicit error capture)...")
    try:
        response = requests.get(f"{base_url}/ping", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:100]}...")
        print("   ✅ Ping endpoint completed")
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
    
    print()
    
    # Test 2: Test 500 error endpoint
    print("🔍 TEST 2: Test 500 error endpoint...")
    try:
        response = requests.get(f"{base_url}/test-500-error", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:100]}...")
        print("   ✅ 500 error endpoint completed")
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
    
    print()
    
    # Test 3: Random unhandled issues
    print("🔍 TEST 3: Random unhandled issues...")
    try:
        response = requests.get(f"{base_url}/test-unhandled-issues", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:100]}...")
        print("   ✅ Random unhandled issues completed")
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
    
    print("\n" + "=" * 60)
    print("💡 EXPECTED SERVER LOGS:")
    print("   For ping endpoint:")
    print("   - 🚀 SENTRY MIDDLEWARE START: GET /ping")
    print("   - 🔍 EXPLICIT ERROR CAPTURE: ZeroDivisionError: division by zero")
    print("   - 🚨 SENTRY MIDDLEWARE CATCH ERROR: GET /ping")
    print("   - 🚀 SENTRY EXCEPTION HANDLER START: GET /ping")
    print("   - ✅ SENTRY EXCEPTION HANDLER END: GET /ping")
    print("   - 🔚 SENTRY MIDDLEWARE END (ERROR): GET /ping")
    print("   - decidninignignggggggggggggggggggggggggggggggg (before_send_filter)")
    print()
    print("🔍 CHECK SERVER CONSOLE FOR THESE LOGS!")

if __name__ == "__main__":
    test_error_capture_fix() 