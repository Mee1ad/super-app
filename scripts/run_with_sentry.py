#!/usr/bin/env python3
"""
Run the server with Sentry middleware to capture errors
"""

import uvicorn
import os
from core.config import settings

def run_with_sentry():
    """Run the server with Sentry middleware"""
    
    print("🚀 Starting server with Sentry Middleware")
    print("=" * 50)
    print(f"Environment: {settings.environment}")
    print(f"Debug mode: {settings.debug}")
    print(f"Sentry environment: {settings.sentry_environment}")
    print(f"Sentry debug: {settings.sentry_debug}")
    print("=" * 50)
    
    # Set environment variables for Sentry
    os.environ["SENTRY_DEBUG"] = "true"
    
    # Run uvicorn with debug settings
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload
        log_level="debug",  # Set log level to debug
        access_log=True,  # Enable access logs
        use_colors=True,  # Enable colored output
    )

if __name__ == "__main__":
    run_with_sentry() 