from typing import Optional
from uuid import UUID
from esmerald import Request, HTTPException, status
from apps.auth.models import User
from apps.auth.services import get_current_user


async def get_current_user_dependency(request: Request) -> User:
    """Dependency to get the current authenticated user from JWT token"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    token = auth_header.split(" ")[1]
    user = await get_current_user(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return user


async def get_current_user_id(request: Request) -> UUID:
    """Dependency to get the current user ID from JWT token"""
    user = await get_current_user_dependency(request)
    return user.id 