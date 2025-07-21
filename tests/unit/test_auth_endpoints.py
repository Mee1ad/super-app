import pytest
from unittest.mock import patch, AsyncMock
from esmerald.testclient import EsmeraldTestClient
from apps.auth.schemas import GoogleAuthRequest, RefreshTokenRequest, TokenResponse
from apps.auth.models import User
from core.security import create_access_token, create_refresh_token


class TestAuthEndpoints:
    """Test authentication endpoints"""

    @pytest.mark.asyncio
    async def test_get_google_auth_url(self, test_client: EsmeraldTestClient):
        """Test getting Google OAuth URL"""
        response = test_client.get("/api/v1/auth/google/url")
        
        assert response.status_code == 200
        data = response.json()
        assert "auth_url" in data
        assert "client_id" in data
        assert "redirect_uri" in data
        assert "accounts.google.com" in data["auth_url"]

    @pytest.mark.asyncio
    async def test_google_login_success(self, test_client: EsmeraldTestClient):
        """Test successful Google OAuth login"""
        from apps.auth.schemas import UserResponse, TokenResponse, LoginResponse
        
        mock_user_response = UserResponse(
            id="550e8400-e29b-41d4-a716-446655440000",
            email="test@example.com",
            username="testuser",
            is_active=True,
            is_superuser=False,
            role_name="user"
        )
        
        mock_token_response = TokenResponse(
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            expires_in=3600
        )
        
        mock_login_response = LoginResponse(
            user=mock_user_response,
            tokens=mock_token_response
        )
        
        with patch('apps.auth.endpoints.authenticate_with_google', new_callable=AsyncMock) as mock_auth:
            mock_auth.return_value = mock_login_response
            
            request_data = GoogleAuthRequest(code="mock_auth_code")
            response = test_client.post("/api/v1/auth/google", json=request_data.model_dump())
            
            assert response.status_code == 201
            data = response.json()
            assert "user" in data
            assert "tokens" in data
            assert data["user"]["email"] == "test@example.com"
            assert "access_token" in data["tokens"]
            assert "refresh_token" in data["tokens"]

    @pytest.mark.asyncio
    async def test_google_login_invalid_code(self, test_client: EsmeraldTestClient):
        """Test Google OAuth login with invalid code"""
        with patch('apps.auth.endpoints.authenticate_with_google', new_callable=AsyncMock) as mock_auth:
            mock_auth.side_effect = ValueError("Failed to exchange code for access token")
            
            request_data = GoogleAuthRequest(code="invalid_code")
            response = test_client.post("/api/v1/auth/google", json=request_data.model_dump())
            
            assert response.status_code == 400
            data = response.json()
            assert "Failed to exchange code for access token" in data["detail"]

    @pytest.mark.asyncio
    async def test_google_login_no_user_info(self, test_client: EsmeraldTestClient):
        """Test Google OAuth login when user info cannot be retrieved"""
        with patch('apps.auth.endpoints.authenticate_with_google', new_callable=AsyncMock) as mock_auth:
            mock_auth.side_effect = ValueError("Failed to get user info from Google")
            
            request_data = GoogleAuthRequest(code="mock_auth_code")
            response = test_client.post("/api/v1/auth/google", json=request_data.model_dump())
            
            assert response.status_code == 400
            data = response.json()
            assert "Failed to get user info from Google" in data["detail"]

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, test_client: EsmeraldTestClient):
        """Test successful token refresh"""
        mock_user = User(
            id="550e8400-e29b-41d4-a716-446655440001",
            email="test@example.com",
            username="testuser",
            hashed_password="",
            is_active=True,
            is_superuser=False
        )
        
        with patch('apps.auth.endpoints.refresh_access_token', new_callable=AsyncMock) as mock_refresh:
            mock_refresh.return_value = TokenResponse(
                access_token="new_access_token",
                refresh_token="new_refresh_token",
                expires_in=3600
            )
            
            request_data = RefreshTokenRequest(refresh_token="valid_refresh_token")
            response = test_client.post("/api/v1/auth/refresh", json=request_data.model_dump())
            
            assert response.status_code == 201
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert "expires_in" in data

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, test_client: EsmeraldTestClient):
        """Test token refresh with invalid refresh token"""
        with patch('apps.auth.endpoints.refresh_access_token', new_callable=AsyncMock) as mock_refresh:
            mock_refresh.side_effect = ValueError("Invalid refresh token")
            
            request_data = RefreshTokenRequest(refresh_token="invalid_refresh_token")
            response = test_client.post("/api/v1/auth/refresh", json=request_data.model_dump())
            
            assert response.status_code == 400
            data = response.json()
            assert "Invalid refresh token" in data["detail"]

    @pytest.mark.asyncio
    async def test_google_callback_success(self, test_client: EsmeraldTestClient):
        """Test Google OAuth callback endpoint"""
        from apps.auth.schemas import UserResponse, TokenResponse, LoginResponse
        
        mock_user_response = UserResponse(
            id="550e8400-e29b-41d4-a716-446655440002",
            email="test@example.com",
            username="testuser",
            is_active=True,
            is_superuser=False,
            role_name="user"
        )
        
        mock_token_response = TokenResponse(
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            expires_in=3600
        )
        
        mock_login_response = LoginResponse(
            user=mock_user_response,
            tokens=mock_token_response
        )
        
        with patch('apps.auth.endpoints.authenticate_with_google', new_callable=AsyncMock) as mock_auth:
            mock_auth.return_value = mock_login_response
            
            response = test_client.get("/api/v1/auth/google/callback?code=mock_auth_code", follow_redirects=False)
            
            assert response.status_code == 302
            assert "Location" in response.headers

    @pytest.mark.asyncio
    async def test_google_callback_error(self, test_client: EsmeraldTestClient):
        """Test Google OAuth callback endpoint with error"""
        with patch('apps.auth.endpoints.authenticate_with_google', new_callable=AsyncMock) as mock_auth:
            mock_auth.side_effect = Exception("OAuth error")
            
            response = test_client.get("/api/v1/auth/google/callback?code=invalid_code", follow_redirects=False)
            
            assert response.status_code == 302
            assert "Location" in response.headers
            assert "error" in response.headers["Location"]


class TestAuthSchemas:
    """Test authentication schemas"""

    def test_google_auth_request_valid(self):
        """Test valid Google auth request"""
        data = {"code": "valid_auth_code"}
        request = GoogleAuthRequest(**data)
        assert request.code == "valid_auth_code"

    def test_google_auth_request_missing_code(self):
        """Test Google auth request with missing code"""
        with pytest.raises(ValueError):
            GoogleAuthRequest()

    def test_refresh_token_request_valid(self):
        """Test valid refresh token request"""
        data = {"refresh_token": "valid_refresh_token"}
        request = RefreshTokenRequest(**data)
        assert request.refresh_token == "valid_refresh_token"

    def test_refresh_token_request_missing_token(self):
        """Test refresh token request with missing token"""
        with pytest.raises(ValueError):
            RefreshTokenRequest()


class TestAuthSecurity:
    """Test authentication security functions"""

    def test_create_access_token(self):
        """Test creating access token"""
        data = {"sub": "user123", "email": "test@example.com"}
        token = create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self):
        """Test creating refresh token"""
        data = {"sub": "user123", "email": "test@example.com"}
        token = create_refresh_token(data)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_different_types(self):
        """Test that access and refresh tokens are different"""
        data = {"sub": "user123", "email": "test@example.com"}
        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)
        assert access_token != refresh_token 