"""
Role-based permissions system
"""
from typing import List, Optional, TYPE_CHECKING
from functools import wraps
from esmerald import HTTPException
from esmerald.requests import Request

if TYPE_CHECKING:
    from apps.auth.models import User


# Permission constants
class Permissions:
    # Changelog permissions
    CHANGELOG_VIEW = "changelog:view"
    CHANGELOG_CREATE = "changelog:create"
    CHANGELOG_UPDATE = "changelog:update"
    CHANGELOG_DELETE = "changelog:delete"
    CHANGELOG_PUBLISH = "changelog:publish"
    CHANGELOG_VIEW_DRAFTS = "changelog:view_drafts"
    
    # Role management
    ROLE_VIEW = "role:view"
    ROLE_CREATE = "role:create"
    ROLE_UPDATE = "role:update"
    ROLE_DELETE = "role:delete"
    
    # User management
    USER_VIEW = "user:view"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"


# Role definitions
DEFAULT_ROLES = {
    "admin": {
        "description": "Full system access",
        "permissions": [
            Permissions.CHANGELOG_VIEW,
            Permissions.CHANGELOG_CREATE,
            Permissions.CHANGELOG_UPDATE,
            Permissions.CHANGELOG_DELETE,
            Permissions.CHANGELOG_PUBLISH,
            Permissions.CHANGELOG_VIEW_DRAFTS,
            Permissions.ROLE_VIEW,
            Permissions.ROLE_CREATE,
            Permissions.ROLE_UPDATE,
            Permissions.ROLE_DELETE,
            Permissions.USER_VIEW,
            Permissions.USER_CREATE,
            Permissions.USER_UPDATE,
            Permissions.USER_DELETE,
        ]
    },
    "editor": {
        "description": "Can manage changelog content",
        "permissions": [
            Permissions.CHANGELOG_VIEW,
            Permissions.CHANGELOG_CREATE,
            Permissions.CHANGELOG_UPDATE,
            Permissions.CHANGELOG_DELETE,
            Permissions.CHANGELOG_VIEW_DRAFTS,
        ]
    },
    "viewer": {
        "description": "Can view published changelog",
        "permissions": [
            Permissions.CHANGELOG_VIEW,
        ]
    }
}


def require_permission(permission: str):
    """Decorator to require a specific permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get user from dependencies
            from core.dependencies import get_current_user_dependency
            
            # Find request in args or kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                for value in kwargs.values():
                    if isinstance(value, Request):
                        request = value
                        break
            
            if not request:
                raise HTTPException(status_code=500, detail="Request object not found")
            
            # Get user using dependency
            try:
                user = await get_current_user_dependency(request)
            except HTTPException:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            # Check permission
            if not user.has_permission(permission):
                raise HTTPException(status_code=403, detail=f"Permission '{permission}' required")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role_name: str):
    """Decorator to require a specific role"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get user from dependencies
            from core.dependencies import get_current_user_dependency
            
            # Find request in args or kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                for value in kwargs.values():
                    if isinstance(value, Request):
                        request = value
                        break
            
            if not request:
                raise HTTPException(status_code=500, detail="Request object not found")
            
            # Get user using dependency
            try:
                user = await get_current_user_dependency(request)
            except HTTPException:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            # Check role
            if not user.has_role(role_name):
                raise HTTPException(status_code=403, detail=f"Role '{role_name}' required")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


async def get_current_user(request: Request) -> Optional["User"]:
    """Get current user from request using dependency injection"""
    from core.dependencies import get_current_user_optional
    return await get_current_user_optional(request)


async def check_permission(user: "User", permission: str) -> bool:
    """Check if user has a specific permission"""
    return user.has_permission(permission)


async def check_role(user: "User", role_name: str) -> bool:
    """Check if user has a specific role"""
    return user.has_role(role_name) 