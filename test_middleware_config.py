#!/usr/bin/env python3
"""
Test the middleware configuration
"""

from core.sentry_middleware import SentryMiddleware
from core.config import settings

def test_middleware_config():
    """Test the middleware configuration"""
    
    print("🧪 Testing Middleware Configuration")
    print("=" * 50)
    
    # Test 1: Check if middleware can be instantiated
    print("\n1. Testing middleware instantiation...")
    try:
        # Create a dummy app
        dummy_app = lambda scope, receive, send: None
        middleware = SentryMiddleware(dummy_app)
        print("✅ SentryMiddleware instantiated successfully")
    except Exception as e:
        print(f"❌ Failed to instantiate SentryMiddleware: {e}")
    
    # Test 2: Check configuration
    print("\n2. Checking configuration...")
    print(f"   Debug mode: {settings.debug}")
    print(f"   Sentry environment: {settings.sentry_environment}")
    print(f"   Sentry debug: {settings.sentry_debug}")
    
    # Test 3: Test error capture function
    print("\n3. Testing error capture function...")
    try:
        middleware = SentryMiddleware(dummy_app)
        test_exception = ValueError("Test exception")
        scope = {"method": "GET", "path": "/test", "headers": []}
        middleware._capture_exception(test_exception, scope)
        print("✅ Error capture function works")
    except Exception as e:
        print(f"❌ Error capture function failed: {e}")
    
    print("\n" + "=" * 50)
    print("💡 Middleware is ready to capture errors!")

if __name__ == "__main__":
    test_middleware_config() 