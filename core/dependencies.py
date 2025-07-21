from typing import Optional, TYPE_CHECKING
from uuid import UUID
from esmerald import Request, HTTPException, status

if TYPE_CHECKING:
    from apps.auth.models import User


async def get_current_user_dependency(request: Request) -> "User":
    """Dependency to get the current authenticated user from JWT token"""
    import logging
    logger = logging.getLogger(__name__)
    
    from apps.auth.models import User
    from apps.auth.services import get_current_user
    
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning(f"Missing or invalid Authorization header: {auth_header}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        token = auth_header.split(" ")[1]
        logger.debug(f"Processing token for request: {request.method} {request.url.path}")
        
        user = await get_current_user(token)
        
        if not user:
            logger.warning(f"Invalid or expired token for request: {request.method} {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        logger.debug(f"User authenticated successfully: {user.id}")
        return user
    except HTTPException:
        # Re-raise HTTP exceptions as they are expected
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user_dependency: {type(e).__name__}: {e}", exc_info=True)
        # Capture error in Sentry
        from core.sentry_utils import capture_error
        capture_error(e, {
            "endpoint": str(request.url.path),
            "method": request.method,
            "error_type": "authentication_error",
            "auth_header_present": bool(request.headers.get("Authorization"))
        })
        raise HTTPException(
            status_code=500,
            detail="Authentication service error"
        )


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