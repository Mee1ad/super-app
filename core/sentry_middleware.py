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
        
        # Add endpoint-specific context
        set_context("endpoint_error", {
            "endpoint": path,
            "method": method,
            "error_type": type(exc).__name__,
            "middleware": "SentryMiddleware",
            "suggestion": "Check endpoint implementation, database connections, and external service dependencies"
        })
        
        # Capture the exception in Sentry with enhanced context
        capture_error(exc, {
            "endpoint": path,
            "method": method,
            "middleware": "SentryMiddleware",
            "error_category": "application_error"
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
        
        # Create a proper exception for HTTP errors with full context
        from core.sentry_utils import capture_error, set_context
        import traceback
        
        # Create descriptive error titles based on status code and path
        def get_error_title(status_code: int, method: str, path: str) -> str:
            """Generate descriptive error titles for Sentry"""
            
            # Common error patterns
            if status_code == 404:
                if path.startswith('/.git/'):
                    return f"Git Repository Access Attempt: {method} {path}"
                elif path.startswith('/api/'):
                    return f"Missing API Endpoint: {method} {path}"
                elif path.startswith('/admin/'):
                    return f"Admin Panel Access Attempt: {method} {path}"
                elif path.startswith('/wp-'):
                    return f"WordPress Scanner Detected: {method} {path}"
                elif path.startswith('/php'):
                    return f"PHP Scanner Detected: {method} {path}"
                elif path.startswith('/.env'):
                    return f"Environment File Access Attempt: {method} {path}"
                elif path.startswith('/config/'):
                    return f"Configuration Access Attempt: {method} {path}"
                else:
                    return f"Resource Not Found: {method} {path}"
            
            elif status_code == 422:
                return f"Validation Error: {method} {path}"
            
            elif status_code == 401:
                return f"Authentication Required: {method} {path}"
            
            elif status_code == 403:
                return f"Access Forbidden: {method} {path}"
            
            elif status_code == 500:
                return f"Internal Server Error: {method} {path}"
            
            elif status_code == 502:
                return f"Bad Gateway: {method} {path}"
            
            elif status_code == 503:
                return f"Service Unavailable: {method} {path}"
            
            elif status_code == 429:
                return f"Rate Limit Exceeded: {method} {path}"
            
            else:
                return f"HTTP {status_code} Error: {method} {path}"
        
        # Create a custom exception with detailed information
        class HTTPError(Exception):
            def __init__(self, status_code: int, method: str, path: str, headers: dict):
                self.status_code = status_code
                self.method = method
                self.path = path
                self.headers = headers
                self.title = get_error_title(status_code, method, path)
                super().__init__(self.title)
        
        # Create the exception
        http_error = HTTPError(status_code, method, path, headers)
        
        # Filter out common HTTP errors that don't need Sentry tracking
        if status_code in [405, 406, 415, 416, 418]:
            # These are client errors that are common and not actionable
            logger.debug(f"HTTP {status_code} ignored: {method} {path}")
            return
        
        # Filter out common 404 errors that are expected and not actionable
        if status_code == 404:
            # Debug logging for 404 filtering
            if settings.debug:
                print(f"🔍 Checking 404 filter for: {method} {path}")
                print(f"   Path length: {len(path)}")
                print(f"   Path starts with '/.env': {path.lower().startswith('/.env')}")
            common_404_paths = [
                '/favicon.ico',
                '/robots.txt',
                '/apple-touch-icon.png',
                '/apple-touch-icon-precomposed.png',
                '/manifest.json',
                '/service-worker.js',
                '/sitemap.xml',
                '/.well-known/security.txt',
                '/.well-known/host-meta',
                '/.well-known/webfinger',
                '/humans.txt',
                '/crossdomain.xml',
                '/clientaccesspolicy.xml',
                '/.git/',
                '/.gitignore',
                '/.env',
                '/wp-',
                '/php',
                '/admin/',
                '/config/',
                '/backup/',
                '/old/',
                '/test/',
                '/tmp/',
                '/temp/'
            ]
            
            # Check if this is a common 404 path
            for common_path in common_404_paths:
                if path.lower().startswith(common_path.lower()):
                    logger.debug(f"Common 404 ignored: {method} {path} (matches {common_path})")
                    return
            
            # Additional check for exact matches and common patterns
            if path.lower() in ['/.env', '/.git', '/.gitignore', '/robots.txt', '/favicon.ico']:
                logger.debug(f"Common 404 ignored (exact match): {method} {path}")
                return
        
        # Add debugging information for specific error codes
        if status_code == 404:
            # This is an actionable 404 (not filtered out above)
            # Get available routes for debugging
            try:
                from main import app
                available_routes = []
                for route in app.routes:
                    if hasattr(route, 'path'):
                        available_routes.append(route.path)
                    elif hasattr(route, 'routes'):
                        # Handle nested routes
                        for nested_route in route.routes:
                            if hasattr(nested_route, 'path'):
                                available_routes.append(f"{route.path}{nested_route.path}")
                
                # Add route debugging info to context
                set_context("debug_404", {
                    "requested_path": path,
                    "requested_method": method,
                    "available_routes": available_routes,
                    "suggestion": "This is an actionable 404 error. Check if the endpoint exists or if authentication is required.",
                    "note": "Common 404s (favicon.ico, robots.txt, etc.) are automatically filtered out."
                })
            except Exception as e:
                # If we can't get routes, just log the error
                logger.warning(f"Could not get available routes for 404 debugging: {e}")
        
        elif status_code == 422:
            # Add debugging information for 422 validation errors
            set_context("debug_422", {
                "requested_path": path,
                "requested_method": method,
                "suggestion": "This is likely a validation error. Check request body, query parameters, or authentication.",
                "common_causes": [
                    "Invalid request body format",
                    "Missing required fields",
                    "Invalid data types",
                    "Authentication token issues",
                    "Database constraint violations"
                ]
            })
        
        # Set context for Sentry
        set_context("request", {
            "method": method,
            "url": path,
            "headers": headers,
        })
        
        # Add breadcrumbs to trace the request flow
        from core.sentry_utils import add_breadcrumb
        add_breadcrumb(
            category="http",
            message=f"HTTP {status_code} error on {method} {path}",
            level="error",
            data={
                "status_code": status_code,
                "method": method,
                "url": path,
                "error_type": "http_error"
            }
        )
        
        set_context("http_error", {
            "endpoint": path,
            "method": method,
            "status_code": status_code,
            "middleware": "SentryMiddleware",
            "error_type": "http_error",
            "response_body": message.get("body", b"").decode("utf-8", errors="ignore") if message.get("body") else None,
            "stack_trace": traceback.format_stack(),
            "error_details": f"HTTP {status_code} error occurred on {method} {path}. This error was captured by the Sentry middleware.",
            "request_headers": dict(headers),
            "response_headers": dict(message.get("headers", [])),
            "query_string": scope.get("query_string", b"").decode("utf-8", errors="ignore"),
            "client": scope.get("client", ["unknown", 0]),
            "server": scope.get("server", ["unknown", 0])
        })
        
        # Capture the exception with full stack trace
        capture_error(http_error, {
            "endpoint": path,
            "method": method,
            "status_code": status_code,
            "middleware": "SentryMiddleware",
            "error_type": "http_error"
        })
        
        logger.error(f"HTTP {status_code} error captured by Sentry middleware: {method} {path}", exc_info=True) 