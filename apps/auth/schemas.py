from pydantic import BaseModel, EmailStr
from typing import Optional

class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponse(BaseModel):
    """User information response"""
    id: str
    email: str
    name: str
    picture: Optional[str] = None
    is_active: bool
    is_verified: bool

class GoogleAuthRequest(BaseModel):
    """Google OAuth authorization code request"""
    code: str

class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str

class LoginResponse(BaseModel):
    """Login response with user and tokens"""
    user: UserResponse
    tokens: TokenResponse 