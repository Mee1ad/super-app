import pytest
from datetime import datetime, timedelta, UTC
from core.config import settings
from core.security import create_access_token, create_refresh_token, verify_token


class TestJWTConfiguration:
    """Test JWT token configuration and expiration times"""
    
    def test_access_token_expiration_time(self):
        """Test that access tokens expire after 30 days (43200 minutes)"""
        assert settings.jwt_access_token_expire_minutes == 43200
        
    def test_refresh_token_expiration_time(self):
        """Test that refresh tokens expire after 30 days"""
        assert settings.jwt_refresh_token_expire_days == 30
        
    def test_access_token_creation_with_default_expiration(self):
        """Test access token creation uses the configured expiration time"""
        user_data = {"sub": "test-user-id", "email": "test@example.com"}
        
        # Create token without custom expiration (should use default)
        token = create_access_token(user_data)
        
        # Verify token
        payload = verify_token(token)
        assert payload is not None
        
        # Check expiration time
        exp_timestamp = payload.get("exp")
        assert exp_timestamp is not None
        
        # Check that expiration is in the future and reasonable
        now = datetime.now(UTC).timestamp()
        expected_min_exp = now + (settings.jwt_access_token_expire_minutes * 60) - 5  # Allow 5 seconds for processing
        expected_max_exp = now + (settings.jwt_access_token_expire_minutes * 60) + 5  # Allow 5 seconds for processing
        
        assert exp_timestamp >= expected_min_exp
        assert exp_timestamp <= expected_max_exp
        
    def test_refresh_token_creation_with_default_expiration(self):
        """Test refresh token creation uses the configured expiration time"""
        user_data = {"sub": "test-user-id", "email": "test@example.com"}
        
        # Create refresh token
        token = create_refresh_token(user_data)
        
        # Verify token
        payload = verify_token(token)
        assert payload is not None
        
        # Check token type
        assert payload.get("type") == "refresh"
        
        # Check expiration time
        exp_timestamp = payload.get("exp")
        assert exp_timestamp is not None
        
        # Check that expiration is in the future and reasonable
        now = datetime.now(UTC).timestamp()
        expected_min_exp = now + (settings.jwt_refresh_token_expire_days * 24 * 60 * 60) - 5  # Allow 5 seconds for processing
        expected_max_exp = now + (settings.jwt_refresh_token_expire_days * 24 * 60 * 60) + 5  # Allow 5 seconds for processing
        
        assert exp_timestamp >= expected_min_exp
        assert exp_timestamp <= expected_max_exp
        
    def test_token_not_expired_immediately(self):
        """Test that newly created tokens are not expired"""
        user_data = {"sub": "test-user-id", "email": "test@example.com"}
        
        access_token = create_access_token(user_data)
        refresh_token = create_refresh_token(user_data)
        
        # Verify tokens are valid
        access_payload = verify_token(access_token)
        refresh_payload = verify_token(refresh_token)
        
        assert access_payload is not None
        assert refresh_payload is not None
        
        # Check that expiration is in the future
        now = datetime.now(UTC).timestamp()
        
        assert access_payload.get("exp") > now
        assert refresh_payload.get("exp") > now 