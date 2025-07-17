from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    model_config = ConfigDict()

class UserResponse(BaseModel):
    """User information response"""
    id: str
    email: str
    username: str
    is_active: bool
    is_superuser: bool
    role_name: Optional[str] = None
    model_config = ConfigDict()

class GoogleAuthRequest(BaseModel):
    """Google OAuth authorization code request"""
    code: str
    model_config = ConfigDict()

class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str
    model_config = ConfigDict()

class LoginResponse(BaseModel):
    """Login response with user and tokens"""
    user: UserResponse
    tokens: TokenResponse
    model_config = ConfigDict() 