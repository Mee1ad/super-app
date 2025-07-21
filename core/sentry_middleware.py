import sentry_sdk
from typing import Any, Dict, Optional, Callable
import logging
import traceback
from core.config import settings
from core.sentry_utils import capture_error, set_context

logger = logging.getLogger(__name__)

class SentryMiddleware:
    """Middleware to capture errors and send them to Sentry"""
    
    def __init__(self, app):
        self.app = app
        # Preserve the original app's methods
        self._preserve_app_methods()
    
    def _preserve_app_methods(self):
        """Preserve the original app's methods and attributes"""
        # Copy all attributes from the original app
        for attr_name in dir(self.app):
            if not attr_name.startswith('_') and not hasattr(self, attr_name):
                try:
                    attr_value = getattr(self.app, attr_name)
                    if callable(attr_value):
                        # Bind the method to preserve 'self' context
                        setattr(self, attr_name, attr_value.__get__(self.app, type(self.app)))
                    else:
                        setattr(self, attr_name, attr_value)
                except AttributeError:
                    # Skip attributes that don't exist or can't be accessed
                    continue
    
    async def __call__(self, scope, receive, send):
        # Get request information from scope
        method = scope.get("method", "UNKNOWN")
        path = scope.get("path", "/")
        
        print(f"🚀 SENTRY MIDDLEWARE START: {method} {path}")
        
        # Create a custom send function to intercept responses
        async def intercept_send(message):
            if message["type"] == "http.response.start":
                status_code = message.get("status", 200)
                if status_code >= 400:
                    print(f"🚨 SENTRY MIDDLEWARE - HTTP ERROR DETECTED: {method} {path} - Status: {status_code}")
                    # Capture HTTP errors that might not raise exceptions
                    self._capture_http_error(status_code, scope, message)
            await send(message)
        
        try:
            # Wrap the entire request processing
            await self.app(scope, receive, intercept_send)
            print(f"✅ SENTRY MIDDLEWARE END (SUCCESS): {method} {path}")
        except Exception as exc:
            print(f"🚨 SENTRY MIDDLEWARE CATCH ERROR: {method} {path}")
            print(f"   Exception: {type(exc).__name__}: {exc}")
            # Capture the exception in Sentry
            self._capture_exception(exc, scope)
            print(f"🔚 SENTRY MIDDLEWARE END (ERROR): {method} {path}")
            raise
        except BaseException as exc:
            # Catch all other exceptions including SystemExit, KeyboardInterrupt
            print(f"🚨 SENTRY MIDDLEWARE CATCH BASE EXCEPTION: {method} {path}")
            print(f"   Exception: {type(exc).__name__}: {exc}")
            # Capture the exception in Sentry
            self._capture_exception(exc, scope)
            print(f"🔚 SENTRY MIDDLEWARE END (BASE ERROR): {method} {path}")
            raise
    
    def _capture_exception(self, exc: Exception, scope: Dict[str, Any]):
        """Capture exception and send to Sentry"""
        
        # Get request information from scope
        method = scope.get("method", "UNKNOWN")
        path = scope.get("path", "/")
        headers = dict(scope.get("headers", []))
        
        # Print debug information
        if settings.debug:
            print("\n" + "="*80)
            print("🚨 SENTRY MIDDLEWARE - ERROR CAPTURED")
            print("="*80)
            print(f"❌ ERROR: {method} {path}")
            print(f"   Exception Type: {type(exc).__name__}")
            print(f"   Exception Message: {exc}")
            print(f"   Headers: {headers}")
            print("\n📋 FULL TRACEBACK:")
            traceback.print_exc()
            print("="*80 + "\n")
        
        # Set context for Sentry
        set_context("request", {
            "method": method,
            "url": path,
            "headers": headers,
        })
        
        # Capture the exception in Sentry
        capture_error(exc, {
            "endpoint": path,
            "method": method,
            "middleware": "SentryMiddleware"
        })
        
        logger.error(f"Error captured by Sentry middleware: {exc}", exc_info=True)
    
    def _capture_http_error(self, status_code: int, scope: Dict[str, Any], message: Dict[str, Any]):
        """Capture HTTP errors that don't raise exceptions"""
        
        # Get request information from scope
        method = scope.get("method", "UNKNOWN")
        path = scope.get("path", "/")
        headers = dict(scope.get("headers", []))
        
        # Print debug information
        if settings.debug:
            print("\n" + "="*80)
            print("🚨 SENTRY MIDDLEWARE - HTTP ERROR CAPTURED")
            print("="*80)
            print(f"❌ HTTP ERROR: {method} {path}")
            print(f"   Status Code: {status_code}")
            print(f"   Headers: {headers}")
            print("="*80 + "\n")
        
        # Set context for Sentry
        set_context("request", {
            "method": method,
            "url": path,
            "headers": headers,
        })
        
        # Create a synthetic exception for HTTP errors
        from core.sentry_utils import capture_message
        capture_message(
            f"HTTP {status_code} error on {method} {path}",
            "error",
            {
                "endpoint": path,
                "method": method,
                "status_code": status_code,
                "middleware": "SentryMiddleware",
                "error_type": "http_error"
            }
        )
        
        logger.error(f"HTTP {status_code} error captured by Sentry middleware: {method} {path}") 