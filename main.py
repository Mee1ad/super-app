import asyncio
import sys
import platform

# Fix for Windows event loop issue with psycopg
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from esmerald import Esmerald, Gateway, get, CORSConfig, Include, Request, options
from core.config import settings
from core.sentry import init_sentry
from core.exceptions import sentry_exception_handler
from core.sentry_middleware import SentryMiddleware
from core.sentry_decorator import capture_sentry_errors
from db.session import database
from api.v1.api_v1 import v1_routes
from datetime import datetime
import logging

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
    path="/",
    tags=["Root"],
    summary="API Root",
    description="Root endpoint that provides API information and available endpoints."
)
def root() -> dict:
    """
    Root endpoint providing API information.
    
    Returns:
        dict: API information and available endpoints
    """
    return {
        "message": "LifeHub API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/ping",
            "api": "/api/v1/",
            "documentation": "/openapi",
            "deployment_info": "/deployment"
        },
        "timestamp": datetime.now().isoformat()
    }


@options(
    path="/",
    tags=["Root"],
    summary="CORS Preflight for Root",
    description="Handle CORS preflight requests for the root endpoint."
)
def root_options() -> dict:
    """
    Handle CORS preflight requests for the root endpoint.
    
    Returns:
        dict: Empty response for CORS preflight
    """
    return {}


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
        Gateway(handler=root),
        Gateway(handler=root_options),
        Gateway(handler=ping),
        Gateway(handler=deployment_info),
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