from typing import Optional, Dict, Any
from apps.auth.models import User
from apps.auth.schemas import TokenResponse, UserResponse, LoginResponse
from core.security import (
    create_access_token, 
    create_refresh_token, 
    get_google_user_info, 
    exchange_google_code_for_token
)
from core.config import settings

async def get_or_create_user_from_google(google_user_info: Dict[str, Any]) -> User:
    """Get existing user or create new user from Google OAuth info"""
    email = google_user_info.get("email")
    google_id = google_user_info.get("sub")
    
    if not email or not google_id:
        raise ValueError("Invalid Google user info")
    
    # Try to find existing user by email
    user = await User.objects.filter(email=email).first()
    
    if not user:
        # Create new user
        username = google_user_info.get("name", email.split("@")[0])
        # Ensure username is unique
        base_username = username
        counter = 1
        while await User.objects.filter(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1
        
        user = await User.objects.create(
            email=email,
            username=username,
            hashed_password="",  # OAuth users don't need password
            is_active=True,
            is_superuser=False  # Default to regular user
        )
    
    return user

async def authenticate_with_google(code: str) -> LoginResponse:
    """Authenticate user with Google OAuth code"""
    # Exchange code for access token
    access_token = await exchange_google_code_for_token(code)
    if not access_token:
        raise ValueError("Failed to exchange code for access token")
    
    # Get user info from Google
    google_user_info = await get_google_user_info(access_token)
    if not google_user_info:
        raise ValueError("Failed to get user info from Google")
    
    # Get or create user
    user = await get_or_create_user_from_google(google_user_info)
    
    # Create tokens
    token_data = {
        "sub": str(user.id),
        "email": str(user.email),
        "username": str(user.username)
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # Create response
    user_response = UserResponse(
        id=str(user.id),
        email=str(user.email),
        username=str(user.username),
        is_active=bool(user.is_active),
        is_superuser=bool(user.is_superuser),
        role_name=user.role.name if user.role else None
    )
    
    token_response = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_access_token_expire_minutes * 60
    )
    
    return LoginResponse(user=user_response, tokens=token_response)

async def refresh_access_token(refresh_token: str) -> TokenResponse:
    """Refresh access token using refresh token"""
    from core.security import verify_token
    
    # Verify refresh token
    payload = verify_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise ValueError("Invalid refresh token")
    
    # Get user
    user_id = payload.get("sub")
    user = await User.objects.get(id=user_id)
    if not user or not user.is_active:
        raise ValueError("User not found or inactive")
    
    # Create new tokens
    token_data = {
        "sub": str(user.id),
        "email": str(user.email),
        "username": str(user.username)
    }
    
    new_access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.jwt_access_token_expire_minutes * 60
    )

async def get_current_user(token: str) -> Optional[User]:
    """Get current user from JWT token"""
    from core.security import get_current_user_from_token
    
    user_info = get_current_user_from_token(token)
    if not user_info:
        return None
    
    user = await User.objects.get(id=user_info["id"])
    if not user or not user.is_active:
        return None
    
    return user 