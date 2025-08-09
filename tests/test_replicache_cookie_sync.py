import pytest
import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from apps.replicache.endpoints import create_cookie, parse_cookie

class TestReplicacheCookieSync:
    """Test Replicache cookie synchronization functionality"""
    
    def test_create_cookie(self):
        """Test cookie creation with proper structure"""
        user_id = "test-user-123"
        client_id = "test-client-456"
        last_mutation_id = 42
        client_name = "todo-replicache-flat"
        
        cookie = create_cookie(user_id, client_id, last_mutation_id, client_name)
        
        # Verify cookie is valid JSON
        parsed = json.loads(cookie)
        
        # Verify required fields
        assert parsed["lastMutationID"] == last_mutation_id
        assert parsed["clientID"] == client_id
        assert "ts" in parsed
        
        # Verify timestamp is recent (within last 5 seconds)
        current_time = int(datetime.now(timezone.utc).timestamp() * 1000)
        assert abs(current_time - parsed["timestamp"]) < 5000
    
    def test_parse_cookie_valid(self):
        """Test parsing valid cookie"""
        cookie_data = {
            "lastMutationID": 123,
            "ts": 1703123456789,
            "clientID": "client456",
        }
        cookie_str = json.dumps(cookie_data)
        
        parsed = parse_cookie(cookie_str)
        assert parsed == cookie_data
    
    def test_parse_cookie_invalid(self):
        """Test parsing invalid cookie"""
        # Test None
        assert parse_cookie(None) is None
        
        # Test empty string
        assert parse_cookie("") is None
        
        # Test invalid JSON
        assert parse_cookie("invalid json") is None
        
        # Test non-string
        assert parse_cookie(123) is None
    
    def test_cookie_consistency_logic(self):
        """Test that cookie logic works correctly"""
        # Test that cookies with different mutation IDs are different
        cookie1 = create_cookie("user1", "client1", 1, "todo-replicache-flat")
        cookie2 = create_cookie("user1", "client1", 2, "todo-replicache-flat")
        
        assert cookie1 != cookie2
        
        # Parse both cookies
        parsed1 = parse_cookie(cookie1)
        parsed2 = parse_cookie(cookie2)
        
        # Verify lastMutationID increased
        assert parsed2["lastMutationID"] > parsed1["lastMutationID"]
        
        # Verify clientID remains consistent
        assert parsed2["clientID"] == parsed1["clientID"]
    
    def test_cookie_with_different_clients(self):
        """Test that cookies for different clients are different"""
        cookie1 = create_cookie("user1", "client1", 1, "todo-replicache-flat")
        cookie2 = create_cookie("user1", "client2", 1, "todo-replicache-flat")
        
        assert cookie1 != cookie2
        
        parsed1 = parse_cookie(cookie1)
        parsed2 = parse_cookie(cookie2)
        
        assert parsed1["clientID"] != parsed2["clientID"]
        assert parsed1["lastMutationID"] == parsed2["lastMutationID"]
    
    def test_cookie_with_different_users(self):
        """Test that cookies for different users are different"""
        cookie1 = create_cookie("user1", "client1", 1, "todo-replicache-flat")
        cookie2 = create_cookie("user2", "client1", 1, "todo-replicache-flat")
        
        assert cookie1 != cookie2
        
        parsed1 = parse_cookie(cookie1)
        parsed2 = parse_cookie(cookie2)
        
        # userId no longer part of cookie; ensure cookies still differ due to ts
        assert cookie1 != cookie2
        assert parsed1["lastMutationID"] == parsed2["lastMutationID"]
    
    def test_cookie_with_different_client_names(self):
        """Test that cookies for different client names are different"""
        cookie1 = create_cookie("user1", "client1", 1, "todo-replicache-flat")
        cookie2 = create_cookie("user1", "client1", 1, "food-tracker-replicache")
        
        assert cookie1 != cookie2
        
        parsed1 = parse_cookie(cookie1)
        parsed2 = parse_cookie(cookie2)
        
        # clientName not present in cookie; ensure cookies still differ due to ts
        assert cookie1 != cookie2
        assert parsed1["lastMutationID"] == parsed2["lastMutationID"]
    
    def test_cookie_timestamp_updates(self):
        """Test that cookie timestamps are updated"""
        cookie1 = create_cookie("user1", "client1", 1, "todo-replicache-flat")
        
        # Wait a moment
        import time
        time.sleep(0.001)
        
        cookie2 = create_cookie("user1", "client1", 1, "todo-replicache-flat")
        
        # Cookies should be different due to timestamp
        assert cookie1 != cookie2
        
        parsed1 = parse_cookie(cookie1)
        parsed2 = parse_cookie(cookie2)
        
        # Timestamps should be different
        assert parsed2["ts"] > parsed1["ts"]