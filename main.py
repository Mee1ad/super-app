from esmerald import Esmerald, Gateway, get, CORSConfig, Include
from core.config import settings
from core.sentry import init_sentry
from core.exceptions import sentry_exception_handler
from core.sentry_middleware import SentryMiddleware
from core.sentry_decorator import capture_sentry_errors
from db.session import database
from api.v1.api_v1 import v1_routes
import logging
import sys

# Configure logging based on debug mode
if settings.debug:
    # Debug mode - show all details
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app.log') if settings.is_production else logging.NullHandler()
        ]
    )
    # Set uvicorn access log to DEBUG level
    logging.getLogger("uvicorn.access").setLevel(logging.DEBUG)
    logging.getLogger("uvicorn.error").setLevel(logging.DEBUG)
else:
    # Production mode - minimal logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log') if settings.is_production else logging.NullHandler()
        ]
    )

logger = logging.getLogger(__name__)

# Log startup information
logger.info(f"Starting application in {'DEBUG' if settings.debug else 'PRODUCTION'} mode")
logger.info(f"Environment: {settings.environment}")
logger.info(f"Debug mode: {settings.debug}")

# Initialize Sentry before creating the app
init_sentry()

# Setup global exception handlers to catch all unhandled errors
from core.sentry_utils import setup_global_exception_handlers
setup_global_exception_handlers()

@get(
    path="/ping",
    tags=["Health"],
    summary="Health check",
    description="Simple health check endpoint to verify API availability and status."
)
def ping() -> dict:
    """
    Health check endpoint.
    
    This endpoint provides a simple way to verify that the API is running
    and accessible. Returns basic status information.
    
    Returns:
        dict: Health status with message and timestamp
    """
    logger.info("Health check endpoint called")
    return {"message": "pong", "status": "healthy"}

@get(
    path="/test-sentry-error",
    tags=["Testing"],
    summary="Test Sentry Error",
    description="Intentionally throws an error to test Sentry error capturing."
)
def test_sentry_error() -> dict:
    """
    Test endpoint that intentionally throws an error to verify Sentry integration.
    
    This endpoint is used for testing purposes only to ensure that errors
    are properly captured and reported to Sentry.
    
    Returns:
        dict: This should never be reached as an error is thrown
        
    Raises:
        ValueError: Always raised for testing purposes
    """
    # Intentionally throw an error to test Sentry
    raise ValueError("This is a test error for Sentry integration testing")

@get(
    path="/test-sentry-message",
    tags=["Testing"],
    summary="Test Sentry Message",
    description="Sends a test message to Sentry for testing purposes."
)
def test_sentry_message() -> dict:
    """
    Test endpoint that sends a test message to Sentry.
    
    This endpoint is used for testing purposes only to ensure that messages
    are properly captured and reported to Sentry.
    
    Returns:
        dict: Success message
    """
    from core.sentry_utils import capture_message
    
    capture_message("This is a test message from the API", "info")
    return {"message": "Test message sent to Sentry"}

@get(
    path="/test-sentry-context",
    tags=["Testing"],
    summary="Test Sentry Context",
    description="Sets user context and sends a test message to Sentry."
)
def test_sentry_context() -> dict:
    """
    Test endpoint that sets user context and sends a test message to Sentry.
    
    This endpoint is used for testing purposes only to ensure that user context
    and additional context are properly captured and reported to Sentry.
    
    Returns:
        dict: Success message
    """
    from core.sentry_utils import set_user, set_context, capture_message
    
    # Set user context
    set_user("test-user-123", email="test@example.com", username="testuser")
    
    # Set additional context
    set_context("test_context", {
        "endpoint": "/test-sentry-context",
        "purpose": "testing",
        "timestamp": "2024-01-01T00:00:00Z"
    })
    
    # Send a test message
    capture_message("Test message with user and context", "info")
    
    return {"message": "Test context and message sent to Sentry"}

@get(
    path="/test-500-error",
    tags=["Testing"],
    summary="Test 500 Error Capture",
    description="Intentionally throws an unhandled exception to test Sentry 500 error capturing."
)
def test_500_error() -> dict:
    """
    Test endpoint that intentionally throws an unhandled exception to verify
    that 500 errors are properly captured by Sentry.
    
    This endpoint is used for testing purposes only to ensure that unhandled
    exceptions are properly captured and reported to Sentry.
    
    Returns:
        dict: This should never be reached as an exception is thrown
        
    Raises:
        RuntimeError: Always raised for testing purposes
    """
    # Intentionally throw an unhandled exception to test Sentry 500 error capturing
    raise RuntimeError("This is a test 500 error for Sentry integration testing")

@get(
    path="/test-simple-error",
    tags=["Testing"],
    summary="Test Simple Error",
    description="Simple test endpoint that raises an error to test exception handling."
)
def test_simple_error() -> dict:
    """
    Simple test endpoint that raises an error to test exception handling.
    
    This endpoint is used for testing purposes only to ensure that exceptions
    are properly handled and logged.
    
    Returns:
        dict: This should never be reached as an error is thrown
        
    Raises:
        ValueError: Always raised for testing purposes
    """
    logger.info("Simple error test endpoint called")
    print("🔍 DEBUG: Simple error test endpoint called")
    print("🔍 DEBUG: About to raise ValueError")
    
    # Raise a simple error
    raise ValueError("This is a simple test error")
    
    return {"message": "This should never be reached"}


@get(
    path="/test-ping-error",
    tags=["Testing"],
    summary="Test Ping Error",
    description="Test endpoint that intentionally throws a division by zero error for testing error handling."
)
def test_ping_error() -> dict:
    """
    Test endpoint that intentionally throws a division by zero error for testing.
    
    This endpoint is used for testing purposes only to ensure that errors
    are properly captured and reported to Sentry.
    
    Returns:
        dict: This should never be reached as an error is thrown
        
    Raises:
        ZeroDivisionError: Always raised for testing purposes
    """
    logger.info("Test ping error endpoint called")
    logger.debug("About to trigger division by zero error for testing")
    
    if settings.debug:
        print("🔍 DEBUG: About to trigger division by zero error")
        print("🔍 DEBUG: This should show detailed error information")
    
    try:
        # Intentionally trigger an error for testing
        5 / 0
    except Exception as e:
        # Explicitly capture the error in Sentry
        from core.sentry_utils import capture_error
        print(f"🔍 EXPLICIT ERROR CAPTURE: {type(e).__name__}: {e}")
        capture_error(e, {
            "endpoint": "/test-ping-error",
            "method": "GET",
            "error_type": "division_by_zero",
            "capture_method": "explicit"
        })
        # Re-raise to trigger the exception handler
        raise
    
    return {"message": "This should never be reached"}


@get(
    path="/test-auth-error",
    tags=["Testing"],
    summary="Test Auth Error",
    description="Test endpoint that simulates authentication errors for testing error handling."
)
async def test_auth_error(request: Request) -> dict:
    """
    Test endpoint that simulates authentication errors for testing.
    
    This endpoint is used for testing purposes only to ensure that authentication
    errors are properly captured and reported to Sentry.
    
    Returns:
        dict: Success message if authentication works
        
    Raises:
        HTTPException: If authentication fails
    """
    logger.info("Test auth error endpoint called")
    
    try:
        # Try to get current user - this will trigger authentication flow
        from core.dependencies import get_current_user_dependency
        user = await get_current_user_dependency(request)
        logger.info(f"Authentication successful for user: {user.id}")
        return {"message": "Authentication successful", "user_id": str(user.id)}
    except Exception as e:
        logger.error(f"Authentication error in test endpoint: {type(e).__name__}: {e}", exc_info=True)
        # Capture error in Sentry
        from core.sentry_utils import capture_error
        capture_error(e, {
            "endpoint": "/test-auth-error",
            "method": "GET",
            "error_type": "auth_test_error",
            "auth_header": request.headers.get("Authorization", "missing")
        })
        raise


@get(
    path="/test-lists-debug",
    tags=["Testing"],
    summary="Test Lists Debug",
    description="Test endpoint to debug lists functionality without authentication."
)
async def test_lists_debug() -> dict:
    """
    Test endpoint to debug lists functionality without authentication.
    
    This endpoint is used for testing purposes only to ensure that the lists
    service is working properly without authentication issues.
    
    Returns:
        dict: Debug information about lists service
    """
    logger.info("Test lists debug endpoint called")
    
    try:
        # Test database connection
        from db.session import database
        await database.connect()
        logger.info("Database connection successful")
        
        # Test lists service
        from apps.todo.services import ListService
        list_service = ListService(database)
        logger.info("List service initialized successfully")
        
        # Test getting all lists (this might fail without user_id, but we'll catch the error)
        try:
            # This will likely fail because we don't have a user_id, but we want to see the error
            lists = await list_service.get_all_lists("test-user-id")
            logger.info(f"Retrieved {len(lists)} lists")
            return {"message": "Lists service working", "lists_count": len(lists)}
        except Exception as e:
            logger.warning(f"Expected error in lists service: {type(e).__name__}: {e}")
            return {"message": "Lists service error (expected)", "error": str(e)}
            
    except Exception as e:
        logger.error(f"Error in test_lists_debug: {type(e).__name__}: {e}", exc_info=True)
        # Capture error in Sentry
        from core.sentry_utils import capture_error
        capture_error(e, {
            "endpoint": "/test-lists-debug",
            "method": "GET",
            "error_type": "lists_debug_error"
        })
        return {"message": "Error in lists debug", "error": str(e)}


@get(
    path="/deployment",
    tags=["Deployment"],
    summary="Deployment & Operations Guide",
    description="""# 🚀 Deployment

This API is deployed using Docker containers with automated CI/CD through GitHub Actions and Ansible.

## Production Environment

- **URL**: `http://YOUR_SERVER_IP:8000`
- **Health Check**: `GET /ping`
- **Documentation**: `GET /openapi`

## Deployment Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GitHub Repo   │───▶│  GitHub Actions  │───▶│  Ubuntu Server  │
│                 │    │   (CI/CD)        │    │   (Production)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────┐        ┌─────────────────┐
                       │ GitHub CR   │        │ Docker Container│
                       │ (Registry)  │        │ (Port 8000)     │
                       └─────────────┘        └─────────────────┘
```

## Deployment Components

1. **Docker Containerization**
   - Multi-stage build for optimized images
   - Non-root user for security
   - Health checks and monitoring
   - Docker secrets for sensitive data

2. **Automated CI/CD Pipeline**
   - GitHub Actions workflow on push to main
   - Automatic Docker image building and pushing
   - Ansible playbook for server deployment
   - Zero-downtime deployments

3. **Infrastructure as Code**
   - Ansible playbooks for server setup
   - Docker Compose for container orchestration
   - Automated system updates and security patches

## Environment Variables

- `API_KEY_FILE=/run/secrets/api_key` - API authentication key
- `DB_PASSWORD_FILE=/run/secrets/db_password` - Database password

## Monitoring and Health Checks

- **Health Endpoint**: `GET /ping`
- **Docker Health Check**: Automatic container health monitoring
- **Application Logs**: `docker logs super-app-api`

## Security Features

- Non-root container execution
- Docker secrets for sensitive data
- SSH key-based server access
- Dedicated application user with limited privileges
- CORS configuration for frontend integration

## Development vs Production

| Environment | URL | Database | Authentication |
|-------------|-----|----------|----------------|
| Development | `http://localhost:8000` | Local SQLite | Development keys |
| Production | `http://YOUR_SERVER_IP:8000` | PostgreSQL | Production secrets |

## Troubleshooting

**Common Issues:**
- Port 8000 not accessible: Check firewall settings
- Container not starting: Check Docker logs
- Database connection failed: Verify secrets configuration

**Manual Commands:**
```bash
# Check container status
docker ps

# View application logs
docker logs super-app-api

# Test health endpoint
curl http://localhost:8000/ping

# SSH into server
ssh -i ./secrets/id_rsa postgres@YOUR_SERVER_IP
```"""
)
def deployment_info() -> dict:
    """Deployment and operations documentation endpoint."""
    return {"message": "See the documentation tab for deployment instructions."}

@get(
    path="/test-unhandled-issues",
    tags=["Testing"],
    summary="Test Unhandled Issues",
    description="Test endpoint that demonstrates different types of unhandled issues."
)
def test_unhandled_issues() -> dict:
    """
    Test endpoint that demonstrates different types of unhandled issues.
    
    This endpoint is used for testing purposes only to ensure that different
    types of unhandled exceptions are properly captured by Sentry.
    
    Returns:
        dict: This should never be reached as an exception is thrown
        
    Raises:
        Various exceptions: For testing different error types
    """
    import random
    
    # Randomly choose different types of unhandled issues
    issue_type = random.randint(1, 5)
    
    if issue_type == 1:
        # Type error
        raise TypeError("This is an unhandled TypeError")
    elif issue_type == 2:
        # Attribute error
        raise AttributeError("This is an unhandled AttributeError")
    elif issue_type == 3:
        # Index error
        raise IndexError("This is an unhandled IndexError")
    elif issue_type == 4:
        # Key error
        raise KeyError("This is an unhandled KeyError")
    else:
        # Custom exception
        raise Exception("This is a generic unhandled exception")
    
    return {"message": "This should never be reached"}

# Robust CORS configuration
cors_config = CORSConfig(
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "https://super-app-front.vercel.app",
        "https://api.todomodo.ir"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

app = Esmerald(
    routes=[
        Gateway(handler=ping),
        Gateway(handler=test_sentry_error),
        Gateway(handler=test_sentry_message),
        Gateway(handler=test_sentry_context),
        Gateway(handler=test_500_error),
        Gateway(handler=test_simple_error),
        Gateway(handler=test_ping_error),
        Gateway(handler=test_auth_error),
        Gateway(handler=test_lists_debug),
        Gateway(handler=deployment_info),
        Gateway(handler=test_unhandled_issues),
        # V1 API routes - all under /api/v1/
        Include(routes=v1_routes, path="/api/v1"),
    ],
    cors_config=cors_config,
    enable_openapi=True,
    openapi_url="/openapi",
    title="LifeHub API",
    version="1.0.0",
    exception_handlers={Exception: sentry_exception_handler},
    debug=settings.debug,  # Enable debug mode in Esmerald
    description="""# LifeHub API

A comprehensive REST API for managing todo lists, ideas, diary entries, and food planning with JWT authentication, real-time search, and bulk operations.

## 📚 API Overview

This API provides comprehensive endpoints for:
- Todo list management (CRUD operations)
- Task management with ordering and toggling
- Shopping list functionality
- Ideas and categories management
- Diary entries with mood tracking
- Food planning and meal tracking
- Real-time search capabilities
- Bulk operations for efficiency

All endpoints include proper error handling, validation, and comprehensive documentation.

## 🚀 Deployment

This API is deployed using Docker containers with automated CI/CD through GitHub Actions and Ansible.

### Production Environment

- **URL**: `http://YOUR_SERVER_IP:8000`
- **Health Check**: `GET /ping`
- **Documentation**: `GET /openapi`
- **API Base**: `GET /api/v1/`

### Deployment Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GitHub Repo   │───▶│  GitHub Actions  │───▶│  Ubuntu Server  │
│                 │    │   (CI/CD)        │    │   (Production)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────┐        ┌─────────────────┐
                       │ GitHub CR   │        │ Docker Container│
                       │ (Registry)  │        │ (Port 8000)     │
                       └─────────────┘        └─────────────────┘
```

### Deployment Components

1. **Docker Containerization**
   - Multi-stage build for optimized images
   - Non-root user for security
   - Health checks and monitoring
   - Docker secrets for sensitive data

2. **Automated CI/CD Pipeline**
   - GitHub Actions workflow on push to main
   - Automatic Docker image building and pushing
   - Ansible playbook for server deployment
   - Zero-downtime deployments

3. **Infrastructure as Code**
   - Ansible playbooks for server setup
   - Docker Compose for container orchestration
   - Automated system updates and security patches

### Environment Variables

The application uses Docker secrets for sensitive configuration:

- `API_KEY_FILE=/run/secrets/api_key` - API authentication key
- `DB_PASSWORD_FILE=/run/secrets/db_password` - Database password

### Monitoring and Health Checks

- **Health Endpoint**: `GET /ping` - Returns application status
- **Docker Health Check**: Automatic container health monitoring
- **Application Logs**: Available via `docker logs super-app-api`

### Security Features

- Non-root container execution
- Docker secrets for sensitive data
- SSH key-based server access
- Dedicated application user with limited privileges
- CORS configuration for frontend integration

### Development vs Production

| Environment | URL | Database | Authentication |
|-------------|-----|----------|----------------|
| Development | `http://localhost:8000` | Local SQLite | Development keys |
| Production | `http://YOUR_SERVER_IP:8000` | PostgreSQL | Production secrets |

### Troubleshooting

**Common Issues:**
- Port 8000 not accessible: Check firewall settings
- Container not starting: Check Docker logs
- Database connection failed: Verify secrets configuration

**Manual Commands:**
```bash
# Check container status
docker ps

# View application logs
docker logs super-app-api

# Test health endpoint
curl http://localhost:8000/ping

# SSH into server
ssh -i ./secrets/id_rsa postgres@YOUR_SERVER_IP
```""",
)

# Apply SentryMiddleware to capture errors before exception handler
app = SentryMiddleware(app)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect() 