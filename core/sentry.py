import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from core.config import settings

def init_sentry():
    """Initialize Sentry SDK for error tracking and performance monitoring"""
    if not settings.sentry_dsn:
        print("Sentry DSN not configured, skipping Sentry initialization")
        return
    
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.sentry_environment,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        profiles_sample_rate=settings.sentry_profiles_sample_rate,
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
        debug=settings.debug,
    )
    
    print(f"Sentry initialized for environment: {settings.sentry_environment}") 