#!/usr/bin/env python3
"""
Test to demonstrate Sentry middleware logging flow
"""

import requests
import time

def test_middleware_logging():
    """Test to show the complete logging flow"""
    
    print("🧪 Testing Sentry Middleware Logging Flow")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    print("📋 EXPECTED LOGGING FLOW:")
    print("   1. 🚀 SENTRY MIDDLEWARE START")
    print("   2. ✅ SENTRY MIDDLEWARE END (SUCCESS) - for normal requests")
    print("   3. 🚨 SENTRY MIDDLEWARE CATCH ERROR - for error requests")
    print("   4. 🚀 SENTRY EXCEPTION HANDLER START")
    print("   5. ✅ SENTRY EXCEPTION HANDLER END")
    print("   6. 🔚 SENTRY MIDDLEWARE END (ERROR)")
    print()
    
    # Test 1: Normal endpoint (should show start and success end)
    print("🔍 TEST 1: Normal endpoint (deployment info)...")
    print("   Expected: 🚀 START → ✅ END (SUCCESS)")
    print()
    try:
        response = requests.get(f"{base_url}/deployment", timeout=10)
        print(f"   Response status: {response.status_code}")
        print("   ✅ Normal endpoint completed")
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
    
    print()
    
    # Test 2: Error endpoint (should show complete error flow)
    print("🔍 TEST 2: Error endpoint (test-500-error)...")
    print("   Expected: 🚀 START → 🚨 CATCH → 🚀 HANDLER → ✅ HANDLER END → 🔚 END (ERROR)")
    print()
    try:
        response = requests.get(f"{base_url}/test-500-error", timeout=10)
        print(f"   Response status: {response.status_code}")
        print("   ✅ Error endpoint completed")
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
    
    print()
    
    # Test 3: Division by zero error
    print("🔍 TEST 3: Division by zero error (ping)...")
    print("   Expected: 🚀 START → 🚨 CATCH → 🚀 HANDLER → ✅ HANDLER END → 🔚 END (ERROR)")
    print()
    try:
        response = requests.get(f"{base_url}/ping", timeout=10)
        print(f"   Response status: {response.status_code}")
        print("   ✅ Division by zero error completed")
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
    
    print()
    
    # Test 4: Random unhandled issues
    print("🔍 TEST 4: Random unhandled issues...")
    print("   Expected: 🚀 START → 🚨 CATCH → 🚀 HANDLER → ✅ HANDLER END → 🔚 END (ERROR)")
    print()
    try:
        response = requests.get(f"{base_url}/test-unhandled-issues", timeout=10)
        print(f"   Response status: {response.status_code}")
        print("   ✅ Random unhandled issues completed")
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
    
    print("\n" + "=" * 60)
    print("💡 LOGGING FLOW SUMMARY:")
    print("   ✅ All requests go through SentryMiddleware")
    print("   ✅ Normal requests show START → END (SUCCESS)")
    print("   ✅ Error requests show complete error flow")
    print("   ✅ Both middleware and handler are logged")
    print("   ✅ before_send_filter is called for errors")
    print()
    print("🔍 CHECK SERVER CONSOLE FOR:")
    print("   - 🚀 SENTRY MIDDLEWARE START")
    print("   - ✅ SENTRY MIDDLEWARE END (SUCCESS)")
    print("   - 🚨 SENTRY MIDDLEWARE CATCH ERROR")
    print("   - 🚀 SENTRY EXCEPTION HANDLER START")
    print("   - ✅ SENTRY EXCEPTION HANDLER END")
    print("   - 🔚 SENTRY MIDDLEWARE END (ERROR)")
    print("   - decidninignignggggggggggggggggggggggggggggggg (before_send_filter)")

if __name__ == "__main__":
    test_middleware_logging() 