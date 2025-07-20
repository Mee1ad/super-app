#!/usr/bin/env python3
"""
Test script to trigger 500 error and check if before_send_filter is called
"""

import requests
import time

def test_500_error_capture():
    """Test 500 error capture"""
    
    print("🧪 Testing 500 Error Capture")
    print("=" * 50)
    
    try:
        print("Making request to /test-500-error...")
        response = requests.get("http://localhost:8000/test-500-error", timeout=10)
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    
    print("\n" + "=" * 50)
    print("💡 Check the server console output for:")
    print("   - 'decidninignignggggggggggggggggggggggggggggggg'")
    print("   - '🔍 Sentry before_send_filter called'")
    print("   - '🚨 SENTRY EXCEPTION HANDLER CALLED!'")

if __name__ == "__main__":
    test_500_error_capture() 