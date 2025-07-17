#!/usr/bin/env python3
"""
Test script to verify Sentry integration is working correctly.
This script will make requests to the test endpoints and show the results.
"""

import requests
import time
import sys

def test_sentry_integration():
    """Test Sentry integration by calling test endpoints"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Sentry Integration")
    print("=" * 50)
    
    # Test 1: Test message endpoint
    print("\n1. Testing message capture...")
    try:
        response = requests.get(f"{base_url}/test-sentry-message")
        if response.status_code == 200:
            print("✅ Message test successful")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Message test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Message test error: {e}")
    
    # Test 2: Test context endpoint
    print("\n2. Testing context capture...")
    try:
        response = requests.get(f"{base_url}/test-sentry-context")
        if response.status_code == 200:
            print("✅ Context test successful")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Context test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Context test error: {e}")
    
    # Test 3: Test error endpoint
    print("\n3. Testing error capture...")
    try:
        response = requests.get(f"{base_url}/test-sentry-error")
        print(f"❌ Error test failed (expected): {response.status_code}")
        print(f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print("✅ Error test successful (error was captured)")
        print(f"   Expected error occurred: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Check your Sentry dashboard to see if the events were captured!")
    print("   - You should see 2 messages and 1 error")
    print("   - The error should include stack trace and context")
    print("   - The messages should include user context and additional context")

if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/ping", timeout=5)
        if response.status_code == 200:
            test_sentry_integration()
        else:
            print("❌ Server is not responding correctly")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the server first:")
        print("   python main.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1) 