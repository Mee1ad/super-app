from esmerald import APIException, Request, Response
from esmerald.exceptions import HTTPException
from typing import Any, Dict, Optional
import logging
from core.sentry_utils import capture_error, set_context

logger = logging.getLogger(__name__)

class SentryExceptionHandler:
    """Global exception handler that captures errors and sends them to Sentry"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def __call__(self, request: Request, exc: Exception) -> Response:
        """Handle exceptions and capture them in Sentry"""
        
        # Set request context for Sentry
        set_context("request", {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        })
        
        # Set user context if available
        if hasattr(request, "user") and request.user:
            set_context("user", {
                "id": getattr(request.user, "id", None),
                "email": getattr(request.user, "email", None),
            })
        
        # Capture the exception in Sentry
        capture_error(exc, {
            "endpoint": str(request.url.path),
            "method": request.method,
            "request_id": getattr(request, "request_id", None),
        })
        
        # Log the error
        self.logger.error(
            f"Unhandled exception in {request.method} {request.url.path}: {exc}",
            exc_info=True
        )
        
        # Return appropriate error response
        if isinstance(exc, APIException):
            return Response(
                content={"detail": str(exc.detail)},
                status_code=exc.status_code,
                media_type="application/json"
            )
        elif isinstance(exc, HTTPException):
            return Response(
                content={"detail": str(exc.detail)},
                status_code=exc.status_code,
                media_type="application/json"
            )
        else:
            # Generic 500 error for unhandled exceptions
            return Response(
                content={
                    "detail": "Internal server error",
                    "error_code": "INTERNAL_ERROR",
                    "request_id": getattr(request, "request_id", None)
                },
                status_code=500,
                media_type="application/json"
            )

# Global exception handler instance
sentry_exception_handler = SentryExceptionHandler()

# Custom API exceptions
class ValidationError(APIException):
    """Raised when request validation fails"""
    status_code = 422
    detail = "Validation error"

class AuthenticationError(APIException):
    """Raised when authentication fails"""
    status_code = 401
    detail = "Authentication required"

class AuthorizationError(APIException):
    """Raised when user lacks required permissions"""
    status_code = 403
    detail = "Insufficient permissions"

class NotFoundError(APIException):
    """Raised when a resource is not found"""
    status_code = 404
    detail = "Resource not found"

class ConflictError(APIException):
    """Raised when there's a resource conflict"""
    status_code = 409
    detail = "Resource conflict"

class RateLimitError(APIException):
    """Raised when rate limit is exceeded"""
    status_code = 429
    detail = "Rate limit exceeded" 