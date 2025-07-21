import os
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.argv import ArgvIntegration
from sentry_sdk.integrations.atexit import AtexitIntegration
from sentry_sdk.integrations.dedupe import DedupeIntegration
from sentry_sdk.integrations.excepthook import ExcepthookIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.modules import ModulesIntegration
from sentry_sdk.integrations.stdlib import StdlibIntegration
from sentry_sdk.integrations.threading import ThreadingIntegration
from sentry_sdk.integrations.asyncpg import AsyncPGIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.loguru import LoguruIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from core.config import settings
import logging

logger = logging.getLogger(__name__)

def before_send_filter(event, hint):
    """Filter events before sending to Sentry"""
    
    # Get environment and debug settings from settings object
    environment = settings.sentry_environment
    debug_mode = settings.sentry_debug
    
    print("🔍 Sentry before_send_filter called")
    print(f"   Environment: {environment}")
    print(f"   Debug mode: {debug_mode}")
    print(f"   Event type: {event.get('type', 'unknown')}")
    
    # In development, block all events from being sent to Sentry
    if environment == "development":
        print("   ❌ Development environment: Sentry event blocked")
        logger.debug("Sentry event blocked in development environment")
        return None
    
    # In production, filter out certain events
    if event.get("type") == "transaction":
        print("   ❌ Transaction event filtered out")
        return None
    
    # Filter out framework-level 404 errors (very common and not actionable)
    if event.get("type") == "error":
        exception = event.get("exception", {})
        if exception and isinstance(exception, dict):
            values = exception.get("values", [])
            for value in values:
                if isinstance(value, dict):
                    # Filter out Lilya/Esmerald framework 404s
                    if (value.get("type") == "HTTPException" and 
                        value.get("value") == "Not Found" and
                        "lilya.routing" in str(value.get("stacktrace", {}).get("frames", []))):
                        print("   ❌ Framework 404 error filtered out")
                        logger.debug("Framework 404 error filtered out")
                        return None
                    
                    # Filter out common framework-level 404s
                    if (value.get("type") == "HTTPException" and 
                        value.get("value") == "Not Found"):
                        # Check if it's from framework routing
                        stacktrace = value.get("stacktrace", {})
                        frames = stacktrace.get("frames", [])
                        framework_modules = ["lilya.routing", "esmerald.routing", "starlette.routing"]
                        
                        for frame in frames:
                            if any(module in str(frame.get("module", "")) for module in framework_modules):
                                print("   ❌ Framework routing 404 filtered out")
                                logger.debug("Framework routing 404 filtered out")
                                return None
    
    print("   ✅ Sentry event allowed to be sent")
    logger.debug("Sentry event allowed to be sent")
    return event

def before_breadcrumb_filter(breadcrumb, hint):
    """Filter breadcrumbs before sending to Sentry"""
    
    # Filter out certain breadcrumbs in production
    environment = settings.sentry_environment
    
    # In development, block all breadcrumbs
    if environment == "development":
        return None
    
    if environment == "production":
        # Filter out database queries in production
        if breadcrumb.get("category") == "db":
            return None
    
    return breadcrumb

def init_sentry():
    """Initialize Sentry SDK with comprehensive configuration"""
    
    # Get Sentry configuration from settings
    dsn = settings.sentry_dsn
    environment = settings.sentry_environment
    debug = settings.sentry_debug
    traces_sample_rate = settings.sentry_traces_sample_rate
    profiles_sample_rate = settings.sentry_profiles_sample_rate
    
    if not dsn:
        print("⚠️  SENTRY_DSN not found, skipping Sentry initialization")
        return
    
    print(f"🔧 Initializing Sentry for environment: {environment}")
    
    # Configure Sentry with comprehensive integrations
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        debug=debug,
        traces_sample_rate=traces_sample_rate,
        profiles_sample_rate=profiles_sample_rate,
        before_send=before_send_filter,
        before_breadcrumb=before_breadcrumb_filter,
        integrations=[
            FastApiIntegration(),
            AsyncioIntegration(),
            SqlalchemyIntegration(),
            ArgvIntegration(),
            AtexitIntegration(),
            DedupeIntegration(),
            ExcepthookIntegration(),
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR
            ),
            ModulesIntegration(),
            StdlibIntegration(),
            ThreadingIntegration(),
            AsyncPGIntegration(),
            HttpxIntegration(),
            LoguruIntegration(),
            StarletteIntegration(),
        ],
        # Enable automatic error capture
        auto_enabling_integrations=True,
        # Capture all exceptions automatically
        attach_stacktrace=True,
        # Send default PII
        send_default_pii=True,
        # Enable performance monitoring
        enable_tracing=True,
    )
    
    logger.info(f"Sentry initialized successfully for environment: {environment}")
    print(f"Sentry initialized for environment: {environment}") 