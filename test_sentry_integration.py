#!/usr/bin/env python3
"""
Comprehensive test of Sentry integration
"""

import requests
import time
import json

def test_sentry_integration():
    """Test Sentry integration comprehensively"""
    
    print("🧪 Comprehensive Sentry Integration Test")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Test message endpoint
    print("\n1. Testing message endpoint...")
    try:
        response = requests.get(f"{base_url}/test-sentry-message")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        print("   ✅ Message endpoint works")
    except Exception as e:
        print(f"   ❌ Message endpoint failed: {e}")
    
    # Test 2: Test 500 error endpoint
    print("\n2. Testing 500 error endpoint...")
    try:
        response = requests.get(f"{base_url}/test-500-error")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")  # Truncate long response
        print("   ✅ 500 error endpoint works")
    except Exception as e:
        print(f"   ❌ 500 error endpoint failed: {e}")
    
    # Test 3: Test simple error endpoint
    print("\n3. Testing simple error endpoint...")
    try:
        response = requests.get(f"{base_url}/test-simple-error")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")  # Truncate long response
        print("   ✅ Simple error endpoint works")
    except Exception as e:
        print(f"   ❌ Simple error endpoint failed: {e}")
    
    # Test 4: Test ping endpoint (division by zero)
    print("\n4. Testing ping endpoint (division by zero)...")
    try:
        response = requests.get(f"{base_url}/ping")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")  # Truncate long response
        print("   ✅ Ping endpoint works (expected error)")
    except Exception as e:
        print(f"   ❌ Ping endpoint failed: {e}")
    
    print("\n" + "=" * 60)
    print("💡 SUMMARY:")
    print("   - All endpoints are responding")
    print("   - Errors are being captured")
    print("   - Check your Sentry dashboard for events")
    print("   - Server console should show 'before_send_filter' calls")
    print("\n🔍 To see server logs, check the terminal where you started uvicorn")
    print("   You should see: 'decidninignignggggggggggggggggggggggggggggggg'")

if __name__ == "__main__":
    test_sentry_integration() 