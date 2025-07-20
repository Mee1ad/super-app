#!/usr/bin/env python3
"""
Test the ping endpoint to see detailed error information in console
"""

import requests
import time

def test_ping_error():
    """Test the ping endpoint to trigger error"""
    
    print("🧪 Testing Ping Endpoint Error")
    print("=" * 50)
    print("This will trigger a division by zero error")
    print("Check the server console for detailed error information")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8000/ping")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Error test completed")
    print("💡 Check the server console for detailed error information")

if __name__ == "__main__":
    test_ping_error() 