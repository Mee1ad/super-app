#!/usr/bin/env python3
"""
Test the Sentry middleware to ensure errors are captured
"""

import requests
import time

def test_sentry_middleware():
    """Test the Sentry middleware"""
    
    print("🧪 Testing Sentry Middleware")
    print("=" * 50)
    
    # Test 1: Test ping endpoint (should trigger division by zero)
    print("\n1. Testing ping endpoint (division by zero)...")
    try:
        response = requests.get("http://localhost:8000/ping")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"   Request failed: {e}")
    
    # Test 2: Test test-500-error endpoint
    print("\n2. Testing test-500-error endpoint...")
    try:
        response = requests.get("http://localhost:8000/test-500-error")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"   Request failed: {e}")
    
    # Test 3: Test test-simple-error endpoint
    print("\n3. Testing test-simple-error endpoint...")
    try:
        response = requests.get("http://localhost:8000/test-simple-error")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"   Request failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Check your Sentry dashboard now!")
    print("💡 You should see:")
    print("   - '🚨 SENTRY MIDDLEWARE - ERROR CAPTURED' in console")
    print("   - Errors in your Sentry dashboard")
    print("   - Detailed error information")

if __name__ == "__main__":
    test_sentry_middleware() 