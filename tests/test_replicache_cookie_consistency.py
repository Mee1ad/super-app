import pytest
import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from apps.replicache.endpoints import create_cookie, parse_cookie

class TestReplicacheCookieConsistency:
    """Test Replicache cookie consistency fix"""
    
    def test_cookie_last_mutation_id_consistency(self):
        """Test that cookie lastMutationID matches the highest mutation ID in changes"""
        # Simulate a scenario where we have multiple mutation IDs
        mutation_changes = {
            "client1": 1,
            "client2": 5,
            "client3": 3
        }
        
        # The cookie should use the highest mutation ID (5)
        highest_mutation_id = max(mutation_changes.values())
        
        user_id = "test-user-123"
        client_id = "test-client-456"
        client_name = "todo-replicache-flat"

        cookie = create_cookie(user_id, client_id, highest_mutation_id, client_name)
        parsed = json.loads(cookie)
        
        # Verify the cookie's lastMutationID matches the highest value
        assert parsed["lastMutationID"] == 5
        assert parsed["lastMutationID"] == highest_mutation_id
    
    def test_cookie_consistency_with_no_changes(self):
        """Test that cookie is consistent when there are no changes"""
        # When there are no changes, lastMutationIDChanges should be empty
        mutation_changes = {}
        
        user_id = "test-user-123"
        client_id = "test-client-456"
        client_name = "todo-replicache-flat"
        current_mutation_id = 0

        # The cookie should use the current mutation ID when no changes
        cookie = create_cookie(user_id, client_id, current_mutation_id, client_name)
        parsed = json.loads(cookie)
        
        # Verify the cookie's lastMutationID matches the current value
        assert parsed["lastMutationID"] == 0
        assert parsed["lastMutationID"] == current_mutation_id
    
    def test_cookie_consistency_with_single_change(self):
        """Test that cookie is consistent with a single mutation change"""
        # Simulate a single mutation change
        mutation_changes = {
            "client1": 42
        }
        
        highest_mutation_id = max(mutation_changes.values())
        
        user_id = "test-user-123"
        client_id = "test-client-456"
        client_name = "todo-replicache-flat"

        cookie = create_cookie(user_id, client_id, highest_mutation_id, client_name)
        parsed = json.loads(cookie)
        
        # Verify the cookie's lastMutationID matches the mutation ID
        assert parsed["lastMutationID"] == 42
        assert parsed["lastMutationID"] == highest_mutation_id
    
    def test_cookie_timestamp_updates_with_changes(self):
        """Test that cookie timestamp updates when there are changes"""
        user_id = "test-user-123"
        client_id = "test-client-456"
        client_name = "todo-replicache-flat"
        mutation_id = 5

        # Create first cookie
        cookie1 = create_cookie(user_id, client_id, mutation_id, client_name)
        parsed1 = json.loads(cookie1)
        timestamp1 = parsed1["ts"]
        
        # Wait a moment
        import time
        time.sleep(0.001)
        
        # Create second cookie with same mutation ID
        cookie2 = create_cookie(user_id, client_id, mutation_id, client_name)
        parsed2 = json.loads(cookie2)
        timestamp2 = parsed2["ts"]
        
        # Timestamps should be different even with same mutation ID
        assert timestamp2 > timestamp1
        
        # But lastMutationID should be the same
        assert parsed1["lastMutationID"] == parsed2["lastMutationID"]
    
    def test_cookie_consistency_across_multiple_clients(self):
        """Test that cookie consistency works across multiple clients"""
        # Simulate multiple clients with different mutation IDs
        mutation_changes = {
            "client1": 10,
            "client2": 25,
            "client3": 15,
            "client4": 30
        }
        
        highest_mutation_id = max(mutation_changes.values())
        
        user_id = "test-user-123"
        client_id = "test-client-456"
        client_name = "todo-replicache-flat"

        cookie = create_cookie(user_id, client_id, highest_mutation_id, client_name)
        parsed = json.loads(cookie)
        
        # Verify the cookie's lastMutationID is the highest among all clients
        assert parsed["lastMutationID"] == 30
        assert parsed["lastMutationID"] == highest_mutation_id
        
        # Verify all mutation IDs in changes are <= cookie's lastMutationID
        for mutation_id in mutation_changes.values():
            assert mutation_id <= parsed["lastMutationID"]
    
    def test_cookie_consistency_edge_cases(self):
        """Test cookie consistency with edge cases"""
        # Test with zero mutation ID
        user_id = "test-user-123"
        client_id = "test-client-456"
        client_name = "todo-replicache-flat"
        
        cookie = create_cookie(user_id, client_id, 0, client_name)
        parsed = json.loads(cookie)
        assert parsed["lastMutationID"] == 0
        
        # Test with very high mutation ID
        cookie = create_cookie(user_id, client_id, 999999, client_name)
        parsed = json.loads(cookie)
        assert parsed["lastMutationID"] == 999999
        
        # Test with negative mutation ID (should still work)
        cookie = create_cookie(user_id, client_id, -1, client_name)
        parsed = json.loads(cookie)
        assert parsed["lastMutationID"] == -1
    
    def test_cookie_structure_remains_valid(self):
        """Test that cookie structure remains valid after consistency fix"""
        user_id = "test-user-123"
        client_id = "test-client-456"
        client_name = "todo-replicache-flat"
        mutation_id = 42

        cookie = create_cookie(user_id, client_id, mutation_id, client_name)
        parsed = json.loads(cookie)
        
        # Verify all required fields are present in canonical cookie
        required_fields = ["lastMutationID", "ts", "clientID"]
        for field in required_fields:
            assert field in parsed
        
        # Verify field types
        assert isinstance(parsed["lastMutationID"], int)
        assert isinstance(parsed["ts"], int)
        assert isinstance(parsed["clientID"], str)
        
        # Verify values
        assert parsed["lastMutationID"] == mutation_id
        assert parsed["clientID"] == client_id
        
        # Verify timestamp is recent
        current_time = int(datetime.now(timezone.utc).timestamp() * 1000)
        assert abs(current_time - parsed["ts"]) < 5000