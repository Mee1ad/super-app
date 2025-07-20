#!/usr/bin/env python3
"""
Test the exception handler to ensure it's working properly
"""

import requests
import time

def test_exception_handler():
    """Test the exception handler"""
    
    print("🧪 Testing Exception Handler")
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
    
    print("\n" + "=" * 50)
    print("💡 Check the server console for detailed error information")
    print("💡 If you don't see detailed errors, the exception handler may not be working")

if __name__ == "__main__":
    test_exception_handler() 