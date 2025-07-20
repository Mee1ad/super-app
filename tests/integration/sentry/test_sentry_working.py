#!/usr/bin/env python3
"""
Test script to verify Sentry is working properly.
This script will test error capture and show detailed debugging information.
"""

import os
import sys
import requests
import time

def test_sentry_working():
    """Test Sentry integration by calling test endpoints"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Sentry Error Capture")
    print("=" * 50)
    
    # Test 1: Test 500 error endpoint
    print("\n1. Testing 500 error capture...")
    try:
        response = requests.get(f"{base_url}/test-500-error")
        print(f"   Expected 500 error: {response.status_code}")
        print(f"   Response: {response.text}")
        print("✅ 500 error test completed - check Sentry dashboard")
    except Exception as e:
        print(f"❌ 500 error test failed: {e}")
    
    # Test 2: Test Sentry error endpoint
    print("\n2. Testing Sentry error endpoint...")
    try:
        response = requests.get(f"{base_url}/test-sentry-error")
        print(f"   Expected error: {response.status_code}")
        print(f"   Response: {response.text}")
        print("✅ Sentry error test completed - check Sentry dashboard")
    except Exception as e:
        print(f"❌ Sentry error test failed: {e}")
    
    # Test 3: Test message endpoint
    print("\n3. Testing message capture...")
    try:
        response = requests.get(f"{base_url}/test-sentry-message")
        if response.status_code == 200:
            print("✅ Message test successful")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Message test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Message test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Check your Sentry dashboard to see if the events were captured!")
    print("💡 If you don't see events, check your environment variables:")
    print("   - SENTRY_DSN")
    print("   - SENTRY_ENVIRONMENT")
    print("   - SENTRY_DEBUG")

if __name__ == "__main__":
    test_sentry_working() 