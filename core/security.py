# OAuth2/JWT and security logic
from datetime import datetime, timedelta, UTC
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import httpx
from core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=settings.jwt_refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        logger.debug("Token verified successfully")
        return payload
    except JWTError as e:
        logger.warning(f"JWT verification failed: {type(e).__name__}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in verify_token: {type(e).__name__}: {e}", exc_info=True)
        # Capture error in Sentry
        from core.sentry_utils import capture_error
        capture_error(e, {
            "function": "verify_token",
            "error_type": "jwt_error",
            "token_length": len(token) if token else 0
        })
        return None

def get_current_user_from_token(token: str) -> Optional[Dict[str, Any]]:
    """Get current user from JWT token"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        payload = verify_token(token)
        if payload is None:
            logger.warning("Token verification failed - no payload")
            return None
        
        user_id: str = payload.get("sub", "")
        if not user_id:
            logger.warning("Token payload missing 'sub' field")
            return None
        
        logger.debug(f"Token verified successfully for user: {user_id}")
        return {
            "id": user_id,
            "email": payload.get("email"),
            "name": payload.get("name"),
            "picture": payload.get("picture")
        }
    except Exception as e:
        logger.error(f"Error in get_current_user_from_token: {type(e).__name__}: {e}", exc_info=True)
        # Capture error in Sentry
        from core.sentry_utils import capture_error
        capture_error(e, {
            "function": "get_current_user_from_token",
            "error_type": "security_error",
            "token_length": len(token) if token else 0
        })
        return None

async def get_google_user_info(access_token: str) -> Optional[Dict[str, Any]]:
    """Get user info from Google using access token"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if response.status_code == 200:
                user_info = response.json()
                return {
                    "email": user_info.get("email"),
                    "name": user_info.get("name"),
                    "picture": user_info.get("picture"),
                    "sub": user_info.get("id")
                }
    except Exception:
        pass
    return None

async def exchange_google_code_for_token(code: str) -> Optional[str]:
    """Exchange authorization code for access token"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.google_redirect_uri
                }
            )
            if response.status_code == 200:
                token_data = response.json()
                return token_data.get("access_token")
    except Exception:
        pass
    return None 