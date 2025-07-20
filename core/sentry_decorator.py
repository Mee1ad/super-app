import functools
import logging
from core.sentry_utils import capture_error, set_context
from core.config import settings
import traceback

logger = logging.getLogger(__name__)

def capture_sentry_errors(func):
    """Decorator to capture errors and send them to Sentry"""
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as exc:
            _capture_error(exc, func.__name__, "async")
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            _capture_error(exc, func.__name__, "sync")
            raise
    
    # Return async wrapper if the function is async, otherwise sync wrapper
    if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:  # CO_COROUTINE flag
        return async_wrapper
    return sync_wrapper

def _capture_error(exc: Exception, function_name: str, function_type: str):
    """Capture error and send to Sentry"""
    
    print(f"🚨 SENTRY DECORATOR - ERROR CAPTURED")
    print(f"   Function: {function_name} ({function_type})")
    print(f"   Exception: {type(exc).__name__}: {exc}")
    
    if settings.debug:
        print("\n📋 FULL TRACEBACK:")
        traceback.print_exc()
        print()
    
    # Set context for Sentry
    set_context("function", {
        "name": function_name,
        "type": function_type,
    })
    
    # Capture the exception in Sentry
    capture_error(exc, {
        "function_name": function_name,
        "function_type": function_type,
        "capture_method": "decorator"
    })
    
    logger.error(f"Error captured by Sentry decorator: {exc}", exc_info=True) 