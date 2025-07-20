#!/usr/bin/env python3
"""
Test the live endpoint to see error details
"""

import httpx
import json

def test_live_endpoint():
    """Test the live ping endpoint"""
    
    print("🧪 Testing Live Ping Endpoint")
    print("=" * 50)
    
    try:
        # Test the ping endpoint
        print("🔍 Making request to http://127.0.0.1:8000/ping")
        response = httpx.get("http://127.0.0.1:8000/ping", timeout=10)
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Headers: {dict(response.headers)}")
        print(f"✅ Content: {response.text}")
        
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
        print(f"❌ Error Response: {e.response.text}")
        
    except httpx.RequestError as e:
        print(f"❌ Request Error: {e}")
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("💡 Live endpoint test completed")

if __name__ == "__main__":
    test_live_endpoint() 