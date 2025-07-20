from esmerald import HTTPException, Request, Response
from esmerald.exceptions import HTTPException as EsmeraldHTTPException
from typing import Any, Dict, Optional
import logging
from core.sentry_utils import capture_error, set_context
import traceback
from core.config import settings

logger = logging.getLogger(__name__)

class SentryExceptionHandler:
    """Global exception handler that captures errors and sends them to Sentry"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        print("🔧 SentryExceptionHandler initialized")
    
    async def __call__(self, request: Request, exc: Exception) -> Response:
        """Handle exceptions and capture them in Sentry"""
        
        print(f"🚀 SENTRY EXCEPTION HANDLER START: {request.method} {request.url.path}")
        print("🚨 SENTRY EXCEPTION HANDLER CALLED!")
        print(f"   Method: {request.method}")
        print(f"   Path: {request.url.path}")
        print(f"   Exception: {type(exc).__name__}: {exc}")
        
        # Log the full error details to console
        self.logger.error(
            f"Unhandled exception in {request.method} {request.url.path}: {exc}",
            exc_info=True
        )
        
        # Print detailed error information in debug mode
        if settings.debug:
            print("\n" + "="*80)
            print("🚨 DEBUG MODE - DETAILED ERROR INFORMATION")
            print("="*80)
            print(f"❌ ERROR: {request.method} {request.url.path}")
            print(f"   Exception Type: {type(exc).__name__}")
            print(f"   Exception Message: {exc}")
            print(f"   Request Headers: {dict(request.headers)}")
            print(f"   Client IP: {request.client.host if request.client else 'Unknown'}")
            print(f"   User Agent: {request.headers.get('user-agent', 'Unknown')}")
            print("\n📋 FULL TRACEBACK:")
            traceback.print_exc()
            print("="*80 + "\n")
        else:
            # Production mode - minimal error output
            print(f"❌ ERROR: {request.method} {request.url.path} - {type(exc).__name__}: {exc}")
        
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
        
        print("🔍 ABOUT TO CALL capture_error - this should trigger before_send_filter")
        # Capture the exception in Sentry
        capture_error(exc, {
            "endpoint": str(request.url.path),
            "method": request.method,
            "request_id": getattr(request, "request_id", None),
            "handler": "SentryExceptionHandler"
        })
        print("🔍 capture_error called - check if before_send_filter was triggered")
        
        # Return appropriate error response
        if isinstance(exc, HTTPException):
            response = Response(
                content={"detail": str(exc.detail)},
                status_code=exc.status_code,
                media_type="application/json"
            )
        elif isinstance(exc, EsmeraldHTTPException):
            response = Response(
                content={"detail": str(exc.detail)},
                status_code=exc.status_code,
                media_type="application/json"
            )
        else:
            # Generic 500 error for unhandled exceptions
            error_detail = str(exc) if settings.debug else "Internal server error"
            response = Response(
                content={
                    "detail": error_detail,
                    "error_code": "INTERNAL_ERROR",
                    "request_id": getattr(request, "request_id", None)
                },
                status_code=500,
                media_type="application/json"
            )
        
        print(f"✅ SENTRY EXCEPTION HANDLER END: {request.method} {request.url.path}")
        return response

# Global exception handler instance
sentry_exception_handler = SentryExceptionHandler()

# Also create a simple function to capture errors directly
def capture_web_error(exc: Exception, method: str = "UNKNOWN", path: str = "/"):
    """Capture web errors directly for cases where exception handler isn't called"""
    
    print(f"🚨 CAPTURING WEB ERROR: {method} {path}")
    print(f"   Exception: {type(exc).__name__}: {exc}")
    
    if settings.debug:
        print("\n📋 FULL TRACEBACK:")
        traceback.print_exc()
        print()
    
    # Set context for Sentry
    set_context("request", {
        "method": method,
        "url": path,
    })
    
    # Capture the exception in Sentry
    capture_error(exc, {
        "endpoint": path,
        "method": method,
        "capture_method": "direct"
    })
    
    logger.error(f"Web error captured directly: {exc}", exc_info=True)

# Custom HTTP exceptions
class ValidationError(HTTPException):
    """Raised when request validation fails"""
    status_code = 422
    detail = "Validation error"

class AuthenticationError(HTTPException):
    """Raised when authentication fails"""
    status_code = 401
    detail = "Authentication required"

class AuthorizationError(HTTPException):
    """Raised when user lacks required permissions"""
    status_code = 403
    detail = "Insufficient permissions"

class NotFoundError(HTTPException):
    """Raised when a resource is not found"""
    status_code = 404
    detail = "Resource not found"

class ConflictError(HTTPException):
    """Raised when there's a resource conflict"""
    status_code = 409
    detail = "Resource conflict"

class RateLimitError(HTTPException):
    """Raised when rate limit is exceeded"""
    status_code = 429
    detail = "Rate limit exceeded" 