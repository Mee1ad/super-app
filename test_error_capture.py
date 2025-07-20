#!/usr/bin/env python3
"""
Simple test to verify error capture is working
"""

import requests
import time

def test_error_capture():
    """Test error capture by calling the test endpoints"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Error Capture")
    print("=" * 50)
    
    # Test 1: Call the test-500-error endpoint
    print("\n1. Testing 500 error endpoint...")
    try:
        response = requests.get(f"{base_url}/test-500-error")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        print("✅ 500 error endpoint called successfully")
    except Exception as e:
        print(f"❌ Error calling endpoint: {e}")
    
    # Test 2: Call the test-sentry-error endpoint
    print("\n2. Testing Sentry error endpoint...")
    try:
        response = requests.get(f"{base_url}/test-sentry-error")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        print("✅ Sentry error endpoint called successfully")
    except Exception as e:
        print(f"❌ Error calling endpoint: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Check your Sentry dashboard now!")
    print("💡 If you don't see errors in Sentry, check:")
    print("   - Your Sentry project settings")
    print("   - Environment filtering in Sentry")
    print("   - Network connectivity")

if __name__ == "__main__":
    test_error_capture() 