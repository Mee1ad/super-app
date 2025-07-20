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
    
    # In development, allow all events to be sent
    if environment == "development":
        print("   ✅ Sentry event allowed to be sent")
        logger.debug("Sentry event allowed to be sent")
        return event
    
    # In production, filter out certain events
    if event.get("type") == "transaction":
        print("   ❌ Transaction event filtered out")
        return None
    
    print("   ✅ Sentry event allowed to be sent")
    logger.debug("Sentry event allowed to be sent")
    return event

def before_breadcrumb_filter(breadcrumb, hint):
    """Filter breadcrumbs before sending to Sentry"""
    
    # Filter out certain breadcrumbs in production
    environment = settings.sentry_environment
    
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
    
    # Test Sentry connection
    try:
        sentry_sdk.capture_message("Sentry connection test message", level="info")
        logger.info("Sentry connection test message sent successfully")
        print("✅ Sentry connection test message sent successfully")
    except Exception as e:
        logger.error(f"Failed to send Sentry test message: {e}")
        print(f"❌ Failed to send Sentry test message: {e}") 