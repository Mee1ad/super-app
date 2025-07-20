#!/usr/bin/env python3
"""
Direct test to see if exceptions are being caught
"""

import sys
import traceback
from core.config import settings

def test_direct_exception():
    """Test exception handling directly"""
    
    print("🧪 Testing Direct Exception Handling")
    print("=" * 50)
    
    try:
        # Simulate the same error as the ping endpoint
        print("🔍 About to trigger division by zero...")
        5 / 0
    except Exception as e:
        print("✅ Exception caught!")
        print(f"   Exception type: {type(e).__name__}")
        print(f"   Exception message: {e}")
        print("\n📋 Full traceback:")
        traceback.print_exc()
        
        if settings.debug:
            print("\n🔍 DEBUG MODE - Additional Information:")
            print(f"   Debug setting: {settings.debug}")
            print(f"   Environment: {settings.environment}")
    
    print("\n" + "=" * 50)
    print("💡 This shows how exceptions should be handled")

if __name__ == "__main__":
    test_direct_exception() 