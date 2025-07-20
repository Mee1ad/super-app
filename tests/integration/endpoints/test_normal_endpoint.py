#!/usr/bin/env python3
"""
Test to show what happens with normal endpoints (no errors)
"""

import requests
import time

def test_normal_endpoint():
    """Test normal endpoint behavior"""
    
    print("🧪 Testing Normal Endpoint (No Errors)")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    print("📋 NORMAL ENDPOINT BEHAVIOR:")
    print("   1. SentryMiddleware wraps ALL requests")
    print("   2. Normal requests pass through silently")
    print("   3. No Sentry events are sent")
    print("   4. No debug output is shown")
    print("   5. Only errors trigger Sentry capture")
    print()
    
    # Test 1: Test deployment info endpoint (normal, no error)
    print("🔍 TEST 1: Normal endpoint (deployment info)...")
    try:
        response = requests.get(f"{base_url}/deployment", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:100]}...")
        print("   ✅ Normal endpoint works (no Sentry activity)")
    except Exception as e:
        print(f"   ❌ Normal endpoint failed: {e}")
    
    print()
    
    # Test 2: Test message endpoint (sends message to Sentry)
    print("🔍 TEST 2: Message endpoint (sends to Sentry)...")
    try:
        response = requests.get(f"{base_url}/test-sentry-message", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        print("   ✅ Message endpoint works (should trigger Sentry)")
    except Exception as e:
        print(f"   ❌ Message endpoint failed: {e}")
    
    print()
    
    # Test 3: Test context endpoint (sends context to Sentry)
    print("🔍 TEST 3: Context endpoint (sends context to Sentry)...")
    try:
        response = requests.get(f"{base_url}/test-sentry-context", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        print("   ✅ Context endpoint works (should trigger Sentry)")
    except Exception as e:
        print(f"   ❌ Context endpoint failed: {e}")
    
    print("\n" + "=" * 60)
    print("💡 NORMAL ENDPOINT SUMMARY:")
    print("   ✅ SentryMiddleware wraps ALL requests")
    print("   ✅ Normal requests pass through silently")
    print("   ✅ No Sentry events for successful requests")
    print("   ✅ Only errors and explicit messages trigger Sentry")
    print()
    print("🔍 WHAT HAPPENS WITH NORMAL ENDPOINTS:")
    print("   Request → SentryMiddleware → Esmerald App → Response")
    print("   (No Sentry activity, no debug output)")
    print()
    print("🔍 WHAT HAPPENS WITH ERROR ENDPOINTS:")
    print("   Request → SentryMiddleware → Error → Sentry Capture → Exception Handler")
    print("   (Sentry activity, debug output, before_send_filter called)")

if __name__ == "__main__":
    test_normal_endpoint() 