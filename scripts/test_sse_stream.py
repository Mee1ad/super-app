#!/usr/bin/env python3
"""
Test script for SSE Stream API
Tests user-specific real-time notifications
"""

import asyncio
import aiohttp
import json
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SSETester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_auth_token(self, user_id: str = "test_user") -> str:
        """Get a test auth token (mock implementation)"""
        # In a real scenario, you'd authenticate with your auth system
        # For testing, we'll use a mock token
        return f"mock_token_for_{user_id}"
    
    async def connect_sse_stream(self, user_id: str) -> aiohttp.ClientResponse:
        """Connect to SSE stream for a user"""
        token = await self.get_auth_token(user_id)
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache"
        }
        
        url = f"{self.base_url}/api/v1/replicache/stream"
        logger.info(f"Connecting to SSE stream: {url}")
        
        response = await self.session.get(url, headers=headers)
        return response
    
    async def poke_user(self, user_id: str) -> dict:
        """Trigger a sync notification for a user"""
        token = await self.get_auth_token(user_id)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/api/v1/replicache/poke-user"
        logger.info(f"Poking user: {url}")
        
        async with self.session.post(url, headers=headers) as response:
            return await response.json()
    
    async def get_stats(self, user_id: str) -> dict:
        """Get SSE connection stats"""
        token = await self.get_auth_token(user_id)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/api/v1/replicache/stats"
        logger.info(f"Getting stats: {url}")
        
        async with self.session.get(url, headers=headers) as response:
            return await response.json()
    
    async def listen_to_stream(self, user_id: str, duration: int = 60):
        """Listen to SSE stream for specified duration"""
        logger.info(f"Starting SSE listener for user {user_id} for {duration} seconds")
        
        try:
            response = await self.connect_sse_stream(user_id)
            
            if response.status != 200:
                logger.error(f"Failed to connect to SSE stream: {response.status}")
                return
            
            logger.info("Successfully connected to SSE stream")
            
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    message = line[6:]  # Remove 'data: ' prefix
                    logger.info(f"Received SSE message: {message}")
                elif line.startswith(':'):
                    logger.debug(f"Received comment: {line}")
                elif line:
                    logger.debug(f"Received other: {line}")
                    
        except Exception as e:
            logger.error(f"Error in SSE stream: {e}")
    
    async def test_user_specific_notifications(self):
        """Test user-specific notifications"""
        logger.info("=== Testing User-Specific SSE Notifications ===")
        
        # Start listening for user1
        user1_task = asyncio.create_task(
            self.listen_to_stream("user1", duration=30)
        )
        
        # Wait a bit for connection to establish
        await asyncio.sleep(2)
        
        # Poke user1 - should receive notification
        logger.info("Poking user1...")
        result = await self.poke_user("user1")
        logger.info(f"Poke result: {result}")
        
        # Wait a bit more
        await asyncio.sleep(5)
        
        # Get stats
        stats = await self.get_stats("user1")
        logger.info(f"Stats: {stats}")
        
        # Cancel the listening task
        user1_task.cancel()
        try:
            await user1_task
        except asyncio.CancelledError:
            pass
        
        logger.info("Test completed")

async def main():
    """Main test function"""
    async with SSETester() as tester:
        await tester.test_user_specific_notifications()

if __name__ == "__main__":
    asyncio.run(main()) 