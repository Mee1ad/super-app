#!/usr/bin/env python3
"""
Test sending a message to Sentry to verify before_send_filter
"""

import requests
import time

def test_sentry_message():
    """Test sending a message to Sentry"""
    
    print("🧪 Testing Sentry Message (should trigger before_send_filter)")
    print("=" * 60)
    
    try:
        print("Making request to /test-sentry-message...")
        response = requests.get("http://localhost:8000/test-sentry-message", timeout=10)
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 200:
            print("✅ Message sent successfully!")
            print("💡 Check the server console for:")
            print("   - 'decidninignignggggggggggggggggggggggggggggggg'")
            print("   - '🔍 Sentry before_send_filter called'")
        else:
            print("❌ Failed to send message")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_sentry_message() 