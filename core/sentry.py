import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from core.config import settings
import logging

logger = logging.getLogger(__name__)

def init_sentry():
    """Initialize Sentry SDK for error tracking and performance monitoring"""
    
    # Debug information
    logger.info(f"Sentry initialization - DSN configured: {bool(settings.sentry_dsn)}")
    logger.info(f"Sentry environment: {settings.sentry_environment}")
    logger.info(f"Debug mode: {settings.sentry_debug}")
    
    if not settings.sentry_dsn:
        logger.warning("Sentry DSN not configured, skipping Sentry initialization")
        print("Sentry DSN not configured, skipping Sentry initialization")
        return
    
    # Validate DSN format
    if not settings.sentry_dsn.startswith('http'):
        logger.error(f"Invalid Sentry DSN format: {settings.sentry_dsn[:20]}...")
        print(f"Invalid Sentry DSN format: {settings.sentry_dsn[:20]}...")
        return
    
    try:
        # Configure sampling rates based on environment
        traces_sample_rate = settings.sentry_traces_sample_rate
        profiles_sample_rate = settings.sentry_profiles_sample_rate
        
        # Reduce sampling in production to avoid overwhelming Sentry
        if settings.sentry_environment == "production":
            traces_sample_rate = min(traces_sample_rate, 0.1)  # Max 10% in production
            profiles_sample_rate = min(profiles_sample_rate, 0.1)  # Max 10% in production
            logger.info(f"Production environment detected - reduced sampling rates: traces={traces_sample_rate}, profiles={profiles_sample_rate}")
        
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.sentry_environment,
            traces_sample_rate=traces_sample_rate,
            profiles_sample_rate=profiles_sample_rate,
            integrations=[
                FastApiIntegration(),
                AsyncioIntegration(),
                SqlalchemyIntegration(),
            ],
            # Enable auto-instrumentation
            auto_enabling_integrations=True,
            # Send default PII
            send_default_pii=True,
            # Enable debug mode in development
            debug=settings.sentry_debug,
            # Additional production settings
            before_send=before_send_filter,
            before_breadcrumb=before_breadcrumb_filter,
            # Release tracking (optional)
            release=os.getenv("SENTRY_RELEASE"),
            # Server name for better identification
            server_name=os.getenv("SENTRY_SERVER_NAME", "unknown"),
        )
        
        logger.info(f"Sentry initialized successfully for environment: {settings.sentry_environment}")
        print(f"Sentry initialized for environment: {settings.sentry_environment}")
        
        # Test Sentry connection
        test_sentry_connection()
        
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")
        print(f"Failed to initialize Sentry: {e}")

def before_send_filter(event, hint):
    """Filter events before sending to Sentry"""
    # Don't send events in development unless explicitly configured
    if settings.sentry_environment == "development" and not settings.sentry_debug:
        return None
    
    # Block all events from localhost/development
    if settings.sentry_environment == "development":
        return None
    
    # Filter out certain error types if needed
    if hint and 'exc_info' in hint:
        exc_type, exc_value, exc_traceback = hint['exc_info']
        # Example: Filter out specific exceptions
        if isinstance(exc_value, KeyboardInterrupt):
            return None
    
    return event

def before_breadcrumb_filter(breadcrumb, hint):
    """Filter breadcrumbs before sending to Sentry"""
    # Don't send breadcrumbs in development unless explicitly configured
    if settings.sentry_environment == "development" and not settings.sentry_debug:
        return None
    
    # Block all breadcrumbs from development
    if settings.sentry_environment == "development":
        return None
    
    return breadcrumb

def test_sentry_connection():
    """Test Sentry connection by sending a test message"""
    try:
        import sentry_sdk
        sentry_sdk.capture_message(
            f"Sentry connection test - Environment: {settings.sentry_environment}",
            level="info"
        )
        logger.info("Sentry connection test message sent successfully")
    except Exception as e:
        logger.error(f"Failed to send Sentry test message: {e}")
        print(f"Failed to send Sentry test message: {e}")

# Import os for release tracking
import os 