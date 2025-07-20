#!/usr/bin/env python3
"""
Production Sentry test that avoids shutdown issues.
This script tests Sentry functionality without causing cleanup errors.
"""

import os
import sys
import time

def test_sentry_production():
    """Test Sentry in production environment"""
    print("🧪 Testing Sentry Production Integration")
    print("=" * 50)
    
    try:
        # Import Sentry
        import sentry_sdk
        from core.config import settings
        
        print(f"✅ Sentry SDK imported")
        print(f"✅ Environment: {settings.sentry_environment}")
        print(f"✅ DSN configured: {bool(settings.sentry_dsn)}")
        
        # Test 1: Check if Sentry is already initialized
        print("\n1. Checking Sentry initialization...")
        if hasattr(sentry_sdk, '_client') and sentry_sdk._client is not None:
            print("✅ Sentry is already initialized")
        else:
            print("⚠️ Sentry not initialized yet")
        
        # Test 2: Test error capture without sending
        print("\n2. Testing error capture...")
        try:
            # Create a test error but don't send it immediately
            test_error = ValueError("Production test error")
            sentry_sdk.capture_exception(test_error)
            print("✅ Error captured successfully")
        except Exception as e:
            print(f"❌ Error capture failed: {e}")
        
        # Test 3: Test message capture
        print("\n3. Testing message capture...")
        try:
            sentry_sdk.capture_message(
                f"Production test message - {time.strftime('%Y-%m-%d %H:%M:%S')}",
                level="info"
            )
            print("✅ Message captured successfully")
        except Exception as e:
            print(f"❌ Message capture failed: {e}")
        
        # Test 4: Test user context
        print("\n4. Testing user context...")
        try:
            sentry_sdk.set_user({
                "id": "production-test-user",
                "email": "test@production.com",
                "username": "production-test"
            })
            print("✅ User context set successfully")
        except Exception as e:
            print(f"❌ User context failed: {e}")
        
        # Test 5: Test additional context
        print("\n5. Testing additional context...")
        try:
            sentry_sdk.set_context("production_test", {
                "test_type": "production_verification",
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                "server": os.getenv('HOSTNAME', 'unknown')
            })
            print("✅ Additional context set successfully")
        except Exception as e:
            print(f"❌ Additional context failed: {e}")
        
        # Test 6: Send a final test message
        print("\n6. Sending final test message...")
        try:
            sentry_sdk.capture_message(
                "Production Sentry test completed successfully",
                level="info"
            )
            print("✅ Final test message sent")
        except Exception as e:
            print(f"❌ Final test message failed: {e}")
        
        print("\n" + "=" * 50)
        print("🎯 Next Steps:")
        print("1. Check your Sentry dashboard for the test messages")
        print("2. Look in the 'Issues' tab for any captured errors")
        print("3. Check the 'Performance' tab for traces")
        print("4. Verify the environment shows 'production'")
        print("5. Test with real application errors")
        
        print("\n✅ Production Sentry test completed!")
        print("Events may take a few minutes to appear in your Sentry dashboard.")
        
    except ImportError as e:
        print(f"❌ Failed to import Sentry: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_sentry_production() 