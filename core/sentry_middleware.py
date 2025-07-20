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
                attr_value = getattr(self.app, attr_name)
                if callable(attr_value):
                    # Bind the method to preserve 'self' context
                    setattr(self, attr_name, attr_value.__get__(self.app, type(self.app)))
                else:
                    setattr(self, attr_name, attr_value)
    
    async def __call__(self, scope, receive, send):
        try:
            await self.app(scope, receive, send)
        except Exception as exc:
            # Capture the exception in Sentry
            self._capture_exception(exc, scope)
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