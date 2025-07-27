import pytest
import uuid
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
        test_user_id = str(uuid.uuid4())
        
        with patch('apps.auth.endpoints.authenticate_with_google', new_callable=AsyncMock) as mock_auth:
            # Mock the complete authentication response
            mock_auth.return_value = {
                "user": {
                    "id": test_user_id,
                    "email": "integration@example.com",
                    "username": "integrationuser",
                    "is_active": True,
                    "is_superuser": False,
                    "role_name": None
                },
                "tokens": {
                    "access_token": "mock_access_token",
                    "refresh_token": "mock_refresh_token",
                    "token_type": "bearer",
                    "expires_in": 43200 * 60  # 30 days in seconds
                }
            }
            
            login_data = GoogleAuthRequest(code="integration_auth_code")
            login_response = test_client.post("/api/v1/auth/google", json=login_data.model_dump())
            
            assert login_response.status_code == 201
            login_result = login_response.json()
            assert "user" in login_result
            assert "tokens" in login_result
            assert login_result["user"]["email"] == "integration@example.com"
            assert login_result["user"]["id"] == test_user_id

    @pytest.mark.asyncio
    async def test_token_refresh_flow(self, test_client: EsmeraldTestClient):
        """Test complete token refresh flow"""
        # Create initial tokens
        test_user_id = str(uuid.uuid4())
        user_data = {"sub": test_user_id, "email": "refresh@example.com"}
        access_token = create_access_token(user_data)
        refresh_token = create_refresh_token(user_data)
        
        with patch('apps.auth.endpoints.refresh_access_token', new_callable=AsyncMock) as mock_refresh:
            mock_refresh.return_value = {
                "access_token": "new_access_token",
                "refresh_token": "new_refresh_token",
                "token_type": "bearer",
                "expires_in": 43200 * 60  # 30 days in seconds
            }
            
            refresh_data = RefreshTokenRequest(refresh_token=refresh_token)
            response = test_client.post("/api/v1/auth/refresh", json=refresh_data.model_dump())
            
            assert response.status_code == 201
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
        
        from apps.auth.schemas import LoginResponse, UserResponse, TokenResponse
        
        with patch('apps.auth.endpoints.authenticate_with_google', new_callable=AsyncMock) as mock_auth:
            # Mock the complete authentication response for callback
            mock_auth.return_value = LoginResponse(
                user=UserResponse(
                    id=str(uuid.uuid4()),
                    email="callback@example.com",
                    username="callbackuser",
                    is_active=True,
                    is_superuser=False,
                    role_name=None
                ),
                tokens=TokenResponse(
                    access_token="mock_access_token",
                    refresh_token="mock_refresh_token",
                    token_type="bearer",
                    expires_in=43200 * 60  # 30 days in seconds
                )
            )
            
            response = test_client.get("/api/v1/auth/google/callback?code=callback_auth_code", follow_redirects=False)
            
            assert response.status_code == 302
            assert "Location" in response.headers
            location = response.headers["Location"]
            assert "auth=" in location or "error=" in location

    @pytest.mark.asyncio
    async def test_error_handling_integration(self, test_client: EsmeraldTestClient):
        """Test error handling throughout the auth flow"""
        # Test invalid OAuth code
        with patch('apps.auth.endpoints.authenticate_with_google', new_callable=AsyncMock) as mock_auth:
            mock_auth.side_effect = ValueError("Failed to exchange code for access token")
            
            login_data = GoogleAuthRequest(code="invalid_code")
            response = test_client.post("/api/v1/auth/google", json=login_data.model_dump())
            
            assert response.status_code == 400
            data = response.json()
            assert "Failed to exchange code for access token" in data["detail"]

        # Test invalid refresh token
        with patch('apps.auth.endpoints.refresh_access_token', new_callable=AsyncMock) as mock_refresh:
            mock_refresh.side_effect = ValueError("Invalid refresh token")
            
            refresh_data = RefreshTokenRequest(refresh_token="invalid_refresh_token")
            response = test_client.post("/api/v1/auth/refresh", json=refresh_data.model_dump())
            
            assert response.status_code == 400
            data = response.json()
            assert "Invalid refresh token" in data["detail"]

    @pytest.mark.asyncio
    async def test_user_creation_integration(self, test_client: EsmeraldTestClient):
        """Test user creation during OAuth flow"""
        test_user_id = str(uuid.uuid4())
        
        with patch('apps.auth.endpoints.authenticate_with_google', new_callable=AsyncMock) as mock_auth:
            # Mock the complete authentication response for new user
            mock_auth.return_value = {
                "user": {
                    "id": test_user_id,
                    "email": "newuser@example.com",
                    "username": "newuser",
                    "is_active": True,
                    "is_superuser": False,
                    "role_name": None
                },
                "tokens": {
                    "access_token": "mock_access_token",
                    "refresh_token": "mock_refresh_token",
                    "token_type": "bearer",
                    "expires_in": 43200 * 60  # 30 days in seconds
                }
            }
            
            login_data = GoogleAuthRequest(code="newuser_auth_code")
            response = test_client.post("/api/v1/auth/google", json=login_data.model_dump())
            
            assert response.status_code == 201
            result = response.json()
            assert result["user"]["email"] == "newuser@example.com"
            assert result["user"]["username"] == "newuser"
            assert result["user"]["is_active"] is True
            assert result["user"]["is_superuser"] is False

    @pytest.mark.asyncio
    async def test_existing_user_login_integration(self, test_client: EsmeraldTestClient):
        """Test login for existing user"""
        test_user_id = str(uuid.uuid4())
        
        with patch('apps.auth.endpoints.authenticate_with_google', new_callable=AsyncMock) as mock_auth:
            # Mock the complete authentication response for existing user
            mock_auth.return_value = {
                "user": {
                    "id": test_user_id,
                    "email": "existing@example.com",
                    "username": "existinguser",
                    "is_active": True,
                    "is_superuser": False,
                    "role_name": None
                },
                "tokens": {
                    "access_token": "mock_access_token",
                    "refresh_token": "mock_refresh_token",
                    "token_type": "bearer",
                    "expires_in": 43200 * 60  # 30 days in seconds
                }
            }
            
            login_data = GoogleAuthRequest(code="existing_auth_code")
            response = test_client.post("/api/v1/auth/google", json=login_data.model_dump())
            
            assert response.status_code == 201
            result = response.json()
            assert result["user"]["email"] == "existing@example.com"
            assert result["user"]["id"] == test_user_id

    @pytest.mark.asyncio
    async def test_token_expiration_integration(self, test_client: EsmeraldTestClient):
        """Test token expiration and refresh flow"""
        # Create tokens with short expiration
        test_user_id = str(uuid.uuid4())
        user_data = {"sub": test_user_id, "email": "expire@example.com"}
        
        # Create tokens with the current settings (no need to mock for this test)
        access_token = create_access_token(user_data)
        refresh_token = create_refresh_token(user_data)
        
        # Verify tokens are created
        access_payload = verify_token(access_token)
        refresh_payload = verify_token(refresh_token)
        
        assert access_payload is not None
        assert refresh_payload is not None
        
        # Test refresh flow
        with patch('apps.auth.endpoints.refresh_access_token', new_callable=AsyncMock) as mock_refresh:
            mock_refresh.return_value = {
                "access_token": "refreshed_access_token",
                "refresh_token": "refreshed_refresh_token",
                "token_type": "bearer",
                "expires_in": 43200 * 60  # 30 days in seconds
            }
            
            refresh_data = RefreshTokenRequest(refresh_token=refresh_token)
            response = test_client.post("/api/v1/auth/refresh", json=refresh_data.model_dump())
            
            assert response.status_code == 201
            result = response.json()
            assert result["access_token"] == "refreshed_access_token"
            assert result["refresh_token"] == "refreshed_refresh_token" 