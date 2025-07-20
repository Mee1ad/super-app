#!/usr/bin/env python3
"""
Enable debug mode and show configuration
"""

import os
from core.config import settings

def enable_debug():
    """Enable debug mode and show configuration"""
    
    print("🔧 Enabling Debug Mode")
    print("=" * 50)
    
    # Set environment variables
    os.environ["DEBUG"] = "true"
    os.environ["SENTRY_DEBUG"] = "true"
    
    print("✅ Environment variables set:")
    print(f"   DEBUG=true")
    print(f"   SENTRY_DEBUG=true")
    
    print("\n📋 Current Configuration:")
    print(f"   Environment: {settings.environment}")
    print(f"   Debug mode: {settings.debug}")
    print(f"   Sentry environment: {settings.sentry_environment}")
    print(f"   Sentry debug: {settings.sentry_debug}")
    
    print("\n🚀 To start server with debug mode:")
    print("   python run_debug.py")
    
    print("\n🧪 To test error capture:")
    print("   python test_ping_error.py")
    
    print("\n💡 Debug mode will show:")
    print("   - Detailed error tracebacks")
    print("   - Request headers and client info")
    print("   - Sentry event filtering details")
    print("   - Full exception information")

if __name__ == "__main__":
    enable_debug() 