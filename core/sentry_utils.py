import sentry_sdk
from typing import Any, Dict, Optional
from functools import wraps
import logging
import sys
import traceback

logger = logging.getLogger(__name__)

def capture_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """Capture and report errors to Sentry"""
    if context:
        sentry_sdk.set_context("error_context", context)
    
    print("🔍 ABOUT TO CALL sentry_sdk.capture_exception - this should trigger before_send_filter")
    # Use capture_exception which will go through before_send_filter
    sentry_sdk.capture_exception(error)
    print("🔍 sentry_sdk.capture_exception called - check if before_send_filter was triggered")
    logger.error(f"Error captured by Sentry: {error}", exc_info=True)

def setup_global_exception_handlers():
    """Setup global exception handlers to catch all unhandled errors"""
    
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Global exception handler for unhandled exceptions"""
        if issubclass(exc_type, KeyboardInterrupt):
            # Don't capture keyboard interrupts
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        print(f"🚨 GLOBAL EXCEPTION HANDLER: {exc_type.__name__}: {exc_value}")
        print("   This is an unhandled exception that wasn't caught by middleware")
        
        # Capture the error in Sentry
        capture_error(exc_value, {
            "error_type": "global_unhandled",
            "exception_type": exc_type.__name__,
            "capture_method": "global_handler"
        })
        
        # Call the original exception hook
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    # Set the global exception handler
    sys.excepthook = handle_exception
    
    print("✅ Global exception handlers setup complete")

def capture_message(message: str, level: str = "info") -> None:
    """Capture and report messages to Sentry"""
    sentry_sdk.capture_message(message, level)
    logger.info(f"Message captured by Sentry: {message}")

def set_user(user_id: str, email: Optional[str] = None, username: Optional[str] = None) -> None:
    """Set user context for Sentry"""
    user_data = {"id": user_id}
    if email:
        user_data["email"] = email
    if username:
        user_data["username"] = username
    sentry_sdk.set_user(user_data)

def clear_user() -> None:
    """Clear user context"""
    sentry_sdk.set_user(None)

def set_context(name: str, context: Dict[str, Any]) -> None:
    """Set additional context for Sentry"""
    sentry_sdk.set_context(name, context)

def add_breadcrumb(
    message: str,
    category: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None,
    level: str = "info"
) -> None:
    """Add breadcrumb for debugging"""
    breadcrumb_data = {
        "message": message,
        "level": level,
    }
    if category:
        breadcrumb_data["category"] = category
    if data:
        breadcrumb_data["data"] = data
    
    sentry_sdk.add_breadcrumb(breadcrumb_data)

def with_sentry(func):
    """Decorator to wrap functions with Sentry error tracking"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            capture_error(e, {
                "function_name": func.__name__,
                "args": str(args),
                "kwargs": str(kwargs)
            })
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            capture_error(e, {
                "function_name": func.__name__,
                "args": str(args),
                "kwargs": str(kwargs)
            })
            raise
    
    # Return async wrapper if the function is async, otherwise sync wrapper
    if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:  # CO_COROUTINE flag
        return async_wrapper
    return sync_wrapper 