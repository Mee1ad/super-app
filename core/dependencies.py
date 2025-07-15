from typing import Optional, TYPE_CHECKING
from uuid import UUID
from esmerald import Request, HTTPException, status

if TYPE_CHECKING:
    from apps.auth.models import User


async def get_current_user_dependency(request: Request) -> "User":
    """Dependency to get the current authenticated user from JWT token"""
    from apps.auth.models import User
    from apps.auth.services import get_current_user
    
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


async def get_current_user_optional(request: Request) -> Optional["User"]:
    """Dependency to get the current user if authenticated, otherwise return None"""
    from apps.auth.services import get_current_user
    
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    try:
        token = auth_header.split(" ")[1]
        user = await get_current_user(token)
        return user if user and user.is_active else None
    except Exception:
        return None


async def get_current_user_id(request: Request) -> UUID:
    """Get current user ID from JWT token"""
    user = await get_current_user_dependency(request)
    return user.id 