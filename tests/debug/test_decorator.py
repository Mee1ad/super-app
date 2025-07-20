#!/usr/bin/env python3
"""
Test the Sentry decorator
"""

from core.sentry_decorator import capture_sentry_errors

@capture_sentry_errors
def test_function():
    """Test function that raises an error"""
    print("🔍 About to raise an error...")
    raise ValueError("Test error from decorator")

def test_decorator():
    """Test the decorator"""
    
    print("🧪 Testing Sentry Decorator")
    print("=" * 50)
    
    try:
        test_function()
    except Exception as e:
        print(f"✅ Exception caught: {e}")
    
    print("\n" + "=" * 50)
    print("💡 Check if you saw the '🚨 SENTRY DECORATOR - ERROR CAPTURED' message")

if __name__ == "__main__":
    test_decorator() 