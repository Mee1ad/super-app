#!/usr/bin/env python3
"""
Test current Sentry configuration and show what's happening
"""

import os
import sys
from core.config import settings
from core.sentry import init_sentry
import sentry_sdk

def test_current_config():
    """Test current Sentry configuration"""
    
    print("🔍 Current Sentry Configuration")
    print("=" * 50)
    
    # Check environment variables
    print("Environment Variables:")
    print(f"  SENTRY_DSN: {os.getenv('SENTRY_DSN', 'Not set')}")
    print(f"  SENTRY_ENVIRONMENT: {os.getenv('SENTRY_ENVIRONMENT', 'Not set')}")
    print(f"  SENTRY_DEBUG: {os.getenv('SENTRY_DEBUG', 'Not set')}")
    
    print("\nSettings Configuration:")
    print(f"  sentry_dsn: {settings.sentry_dsn}")
    print(f"  sentry_environment: {settings.sentry_environment}")
    print(f"  sentry_debug: {settings.sentry_debug}")
    
    print("\nTesting Sentry Initialization:")
    try:
        init_sentry()
        print("✅ Sentry initialized successfully")
        
        # Test error capture
        print("\nTesting Error Capture:")
        try:
            sentry_sdk.capture_exception(ValueError("Test error from script"))
            print("✅ Error captured successfully")
        except Exception as e:
            print(f"❌ Error capture failed: {e}")
            
        # Test message capture
        print("\nTesting Message Capture:")
        try:
            sentry_sdk.capture_message("Test message from script", level="info")
            print("✅ Message captured successfully")
        except Exception as e:
            print(f"❌ Message capture failed: {e}")
            
    except Exception as e:
        print(f"❌ Sentry initialization failed: {e}")
    
    print("\n" + "=" * 50)
    print("💡 To enable Sentry in development, add to your .env file:")
    print("   SENTRY_DSN=your-actual-sentry-dsn")
    print("   SENTRY_DEBUG=true")

if __name__ == "__main__":
    test_current_config() 