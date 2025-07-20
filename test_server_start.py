#!/usr/bin/env python3
"""
Test server startup and basic functionality
"""

import uvicorn
import asyncio
import httpx
import time

def test_server():
    """Test the server startup and basic functionality"""
    
    print("🧪 Testing Server Startup")
    print("=" * 50)
    
    # Start the server in a separate process
    config = uvicorn.Config(
        "main:app",
        host="127.0.0.1",
        port=8000,
        log_level="debug",
        reload=False
    )
    
    server = uvicorn.Server(config)
    
    print("🚀 Starting server...")
    
    # Start server in background
    import threading
    server_thread = threading.Thread(target=server.run)
    server_thread.daemon = True
    server_thread.start()
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    try:
        # Test basic connectivity
        print("🔍 Testing basic connectivity...")
        response = httpx.get("http://127.0.0.1:8000/ping", timeout=5)
        print(f"✅ Response status: {response.status_code}")
        print(f"✅ Response content: {response.text[:200]}...")
        
    except Exception as e:
        print(f"❌ Error testing server: {e}")
    
    print("\n" + "=" * 50)
    print("💡 Server test completed")

if __name__ == "__main__":
    test_server() 