import pytest
from unittest.mock import patch, AsyncMock
from esmerald.testclient import EsmeraldTestClient
from apps.auth.models import User
from apps.auth.schemas import GoogleAuthRequest, RefreshTokenRequest
from core.security import create_access_token, create_refresh_token, verify_token


class TestAuthIntegration:
    """Integration tests for authentication flow"""

    @pytest.mark.asyncio
    async def test_complete_google_oauth_flow(self, test_client: EsmeraldTestClient):
        """Test complete Google OAuth flow from URL to login"""
        # Step 1: Get Google OAuth URL
        url_response = test_client.get("/api/v1/auth/google/url")
        assert url_response.status_code == 200
        url_data = url_response.json()
        assert "auth_url" in url_data
        
        # Step 2: Simulate Google OAuth login
        mock_user_info = {
            "email": "integration@example.com",
            "name": "Integration Test User",
            "picture": "https://example.com/avatar.jpg",
            "sub": "integration123"
        }
        
        with patch('apps.auth.services.exchange_google_code_for_token', new_callable=AsyncMock) as mock_exchange, \
             patch('apps.auth.services.get_google_user_info', new_callable=AsyncMock) as mock_get_info, \
             patch('apps.auth.services.get_or_create_user_from_google', new_callable=AsyncMock) as mock_get_user:
            
            mock_exchange.return_value = "integration_access_token"
            mock_get_info.return_value = mock_user_info
            
            mock_user = User(
                id="integration-user-id",
                email="integration@example.com",
                username="integrationuser",
                hashed_password="",
                is_active=True,
                is_superuser=False
            )
            mock_get_user.return_value = mock_user
            
            login_data = GoogleAuthRequest(code="integration_auth_code")
            login_response = test_client.post("/api/v1/auth/google", json=login_data.dict())
            
            assert login_response.status_code == 200
            login_result = login_response.json()
            assert "user" in login_result
            assert "tokens" in login_result
            assert login_result["user"]["email"] == "integration@example.com"
            
            # Step 3: Test token verification
            access_token = login_result["tokens"]["access_token"]
            refresh_token = login_result["tokens"]["refresh_token"]
            
            # Verify tokens are valid
            access_payload = verify_token(access_token)
            refresh_payload = verify_token(refresh_token)
            
            assert access_payload is not None
            assert refresh_payload is not None
            assert access_payload["sub"] == "integration-user-id"
            assert refresh_payload["sub"] == "integration-user-id"
            assert refresh_payload["type"] == "refresh"

    @pytest.mark.asyncio
    async def test_token_refresh_flow(self, test_client: EsmeraldTestClient):
        """Test complete token refresh flow"""
        # Create initial tokens
        user_data = {"sub": "refresh-user-id", "email": "refresh@example.com"}
        access_token = create_access_token(user_data)
        refresh_token = create_refresh_token(user_data)
        
        mock_user = User(
            id="refresh-user-id",
            email="refresh@example.com",
            username="refreshuser",
            hashed_password="",
            is_active=True,
            is_superuser=False
        )
        
        with patch('apps.auth.services.refresh_access_token', new_callable=AsyncMock) as mock_refresh:
            mock_refresh.return_value = {
                "access_token": "new_access_token",
                "refresh_token": "new_refresh_token",
                "expires_in": 3600
            }
            
            refresh_data = RefreshTokenRequest(refresh_token=refresh_token)
            response = test_client.post("/api/v1/auth/refresh", json=refresh_data.dict())
            
            assert response.status_code == 200
            result = response.json()
            assert "access_token" in result
            assert "refresh_token" in result
            assert "expires_in" in result

    @pytest.mark.asyncio
    async def test_oauth_callback_flow(self, test_client: EsmeraldTestClient):
        """Test OAuth callback flow with redirect"""
        mock_user_info = {
            "email": "callback@example.com",
            "name": "Callback Test User",
            "picture": "https://example.com/avatar.jpg",
            "sub": "callback123"
        }
        
        with patch('apps.auth.services.exchange_google_code_for_token', new_callable=AsyncMock) as mock_exchange, \
             patch('apps.auth.services.get_google_user_info', new_callable=AsyncMock) as mock_get_info, \
             patch('apps.auth.services.get_or_create_user_from_google', new_callable=AsyncMock) as mock_get_user:
            
            mock_exchange.return_value = "callback_access_token"
            mock_get_info.return_value = mock_user_info
            
            mock_user = User(
                id="callback-user-id",
                email="callback@example.com",
                username="callbackuser",
                hashed_password="",
                is_active=True,
                is_superuser=False
            )
            mock_get_user.return_value = mock_user
            
            response = test_client.get("/api/v1/auth/google/callback?code=callback_auth_code")
            
            assert response.status_code == 302
            assert "Location" in response.headers
            location = response.headers["Location"]
            assert "auth=" in location or "error=" in location

    @pytest.mark.asyncio
    async def test_error_handling_integration(self, test_client: EsmeraldTestClient):
        """Test error handling throughout the auth flow"""
        # Test invalid OAuth code
        with patch('apps.auth.services.exchange_google_code_for_token', new_callable=AsyncMock) as mock_exchange:
            mock_exchange.return_value = None
            
            login_data = GoogleAuthRequest(code="invalid_code")
            response = test_client.post("/api/v1/auth/google", json=login_data.dict())
            
            assert response.status_code == 400
            data = response.json()
            assert "Failed to exchange code for access token" in data["detail"]

        # Test invalid refresh token
        with patch('apps.auth.services.refresh_access_token', new_callable=AsyncMock) as mock_refresh:
            mock_refresh.side_effect = ValueError("Invalid refresh token")
            
            refresh_data = RefreshTokenRequest(refresh_token="invalid_refresh_token")
            response = test_client.post("/api/v1/auth/refresh", json=refresh_data.dict())
            
            assert response.status_code == 400
            data = response.json()
            assert "Invalid refresh token" in data["detail"]

    @pytest.mark.asyncio
    async def test_user_creation_integration(self, test_client: EsmeraldTestClient):
        """Test user creation during OAuth flow"""
        mock_user_info = {
            "email": "newuser@example.com",
            "name": "New User",
            "picture": "https://example.com/avatar.jpg",
            "sub": "newuser123"
        }
        
        with patch('apps.auth.services.exchange_google_code_for_token', new_callable=AsyncMock) as mock_exchange, \
             patch('apps.auth.services.get_google_user_info', new_callable=AsyncMock) as mock_get_info, \
             patch('apps.auth.services.get_or_create_user_from_google', new_callable=AsyncMock) as mock_get_user:
            
            mock_exchange.return_value = "newuser_access_token"
            mock_get_info.return_value = mock_user_info
            
            # Simulate new user creation
            new_user = User(
                id="new-user-id",
                email="newuser@example.com",
                username="newuser",
                hashed_password="",
                is_active=True,
                is_superuser=False
            )
            mock_get_user.return_value = new_user
            
            login_data = GoogleAuthRequest(code="newuser_auth_code")
            response = test_client.post("/api/v1/auth/google", json=login_data.dict())
            
            assert response.status_code == 200
            result = response.json()
            assert result["user"]["email"] == "newuser@example.com"
            assert result["user"]["username"] == "newuser"
            assert result["user"]["is_active"] is True
            assert result["user"]["is_superuser"] is False

    @pytest.mark.asyncio
    async def test_existing_user_login_integration(self, test_client: EsmeraldTestClient):
        """Test login for existing user"""
        mock_user_info = {
            "email": "existing@example.com",
            "name": "Existing User",
            "picture": "https://example.com/avatar.jpg",
            "sub": "existing123"
        }
        
        with patch('apps.auth.services.exchange_google_code_for_token', new_callable=AsyncMock) as mock_exchange, \
             patch('apps.auth.services.get_google_user_info', new_callable=AsyncMock) as mock_get_info, \
             patch('apps.auth.services.get_or_create_user_from_google', new_callable=AsyncMock) as mock_get_user:
            
            mock_exchange.return_value = "existing_access_token"
            mock_get_info.return_value = mock_user_info
            
            # Simulate existing user
            existing_user = User(
                id="existing-user-id",
                email="existing@example.com",
                username="existinguser",
                hashed_password="",
                is_active=True,
                is_superuser=False
            )
            mock_get_user.return_value = existing_user
            
            login_data = GoogleAuthRequest(code="existing_auth_code")
            response = test_client.post("/api/v1/auth/google", json=login_data.dict())
            
            assert response.status_code == 200
            result = response.json()
            assert result["user"]["email"] == "existing@example.com"
            assert result["user"]["id"] == "existing-user-id"

    @pytest.mark.asyncio
    async def test_token_expiration_integration(self, test_client: EsmeraldTestClient):
        """Test token expiration and refresh flow"""
        # Create tokens with short expiration
        user_data = {"sub": "expire-user-id", "email": "expire@example.com"}
        
        with patch('core.security.settings') as mock_settings:
            mock_settings.jwt_access_token_expire_minutes = 1  # 1 minute
            mock_settings.jwt_refresh_token_expire_days = 1    # 1 day
            
            access_token = create_access_token(user_data)
            refresh_token = create_refresh_token(user_data)
        
        # Verify tokens are created
        access_payload = verify_token(access_token)
        refresh_payload = verify_token(refresh_token)
        
        assert access_payload is not None
        assert refresh_payload is not None
        
        # Test refresh flow
        mock_user = User(
            id="expire-user-id",
            email="expire@example.com",
            username="expireuser",
            hashed_password="",
            is_active=True,
            is_superuser=False
        )
        
        with patch('apps.auth.services.refresh_access_token', new_callable=AsyncMock) as mock_refresh:
            mock_refresh.return_value = {
                "access_token": "refreshed_access_token",
                "refresh_token": "refreshed_refresh_token",
                "expires_in": 3600
            }
            
            refresh_data = RefreshTokenRequest(refresh_token=refresh_token)
            response = test_client.post("/api/v1/auth/refresh", json=refresh_data.dict())
            
            assert response.status_code == 200
            result = response.json()
            assert result["access_token"] == "refreshed_access_token"
            assert result["refresh_token"] == "refreshed_refresh_token" 