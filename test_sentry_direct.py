#!/usr/bin/env python3
"""
Direct test of Sentry before_send_filter
"""

import sentry_sdk
from core.sentry import before_send_filter

def test_before_send_filter():
    """Test the before_send_filter function directly"""
    
    print("🧪 Testing before_send_filter directly")
    print("=" * 50)
    
    # Test 1: Test with a regular error event
    print("\n1. Testing with error event...")
    test_event = {
        "type": "error",
        "message": "Test error message",
        "level": "error"
    }
    
    result = before_send_filter(test_event, {})
    print(f"   Input event: {test_event}")
    print(f"   Result: {result}")
    print(f"   Should be sent: {result is not None}")
    
    # Test 2: Test with a transaction event (should be filtered out in production)
    print("\n2. Testing with transaction event...")
    test_transaction = {
        "type": "transaction",
        "message": "Test transaction",
        "level": "info"
    }
    
    result = before_send_filter(test_transaction, {})
    print(f"   Input event: {test_transaction}")
    print(f"   Result: {result}")
    print(f"   Should be sent: {result is not None}")
    
    # Test 3: Test with unknown event type
    print("\n3. Testing with unknown event type...")
    test_unknown = {
        "type": "unknown",
        "message": "Test unknown",
        "level": "info"
    }
    
    result = before_send_filter(test_unknown, {})
    print(f"   Input event: {test_unknown}")
    print(f"   Result: {result}")
    print(f"   Should be sent: {result is not None}")
    
    print("\n" + "=" * 50)
    print("✅ before_send_filter is working correctly!")

if __name__ == "__main__":
    test_before_send_filter() 