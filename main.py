from esmerald import Esmerald, Gateway, get, CORSConfig, Include
from core.config import settings
from db.session import database
from apps.todo.endpoints import (
    get_lists, create_list, update_list, delete_list,
    get_tasks, create_task, update_task, delete_task, toggle_task, reorder_tasks,
    get_items, create_item, update_item, delete_item, toggle_item, reorder_items,
    search
)
from apps.ideas.endpoints import (
    get_categories, get_ideas, create_idea, get_idea, update_idea, delete_idea
)
from apps.diary.endpoints import (
    get_moods, get_diary_entries, create_diary_entry, get_diary_entry, 
    update_diary_entry, delete_diary_entry, upload_image
)
from apps.food_planner.endpoints import (
    get_meal_types, get_food_entries, create_food_entry, get_food_entry,
    update_food_entry, delete_food_entry, get_food_summary, get_calendar_data, upload_food_image
)
from apps.auth.endpoints import google_login, refresh_token, get_google_auth_url, google_callback

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
    return {"message": "pong"}

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
        Gateway(handler=ping),
        # Auth endpoints
        Gateway(handler=google_login, path="/api/v1/auth"),
        Gateway(handler=refresh_token, path="/api/v1/auth"),
        Gateway(handler=get_google_auth_url, path="/api/v1/auth"),
        Gateway(handler=google_callback, path="/api/v1/auth/google/callback"),
        # Todo endpoints
        Gateway(handler=get_lists),
        Gateway(handler=create_list),
        Gateway(handler=update_list),
        Gateway(handler=delete_list),
        Gateway(handler=get_tasks),
        Gateway(handler=create_task),
        Gateway(handler=update_task),
        Gateway(handler=delete_task),
        Gateway(handler=toggle_task),
        Gateway(handler=reorder_tasks),
        Gateway(handler=get_items),
        Gateway(handler=create_item),
        Gateway(handler=update_item),
        Gateway(handler=delete_item),
        Gateway(handler=toggle_item),
        Gateway(handler=reorder_items),
        Gateway(handler=search),
        Gateway(handler=get_categories),
        Gateway(handler=get_ideas),
        Gateway(handler=create_idea),
        Gateway(handler=get_idea),
        Gateway(handler=update_idea),
        Gateway(handler=delete_idea),
        Gateway(handler=get_moods),
        Gateway(handler=get_diary_entries),
        Gateway(handler=create_diary_entry),
        Gateway(handler=get_diary_entry),
        Gateway(handler=update_diary_entry),
        Gateway(handler=delete_diary_entry),
        Gateway(handler=upload_image),
        Gateway(handler=get_meal_types),
        Gateway(handler=get_food_entries),
        Gateway(handler=create_food_entry),
        Gateway(handler=get_food_entry),
        Gateway(handler=update_food_entry),
        Gateway(handler=delete_food_entry),
        Gateway(handler=get_food_summary),
        Gateway(handler=get_calendar_data),
        Gateway(handler=upload_food_image),
        Gateway(handler=deployment_info),
    ],
    cors_config=cors_config,
    enable_openapi=True,
    openapi_url="/openapi",
    title="LifeHub API",
    version="1.0.0",
    description="""# LifeHub API

A comprehensive REST API for managing todo lists and shopping lists with JWT authentication, real-time search, and bulk operations.

## 📚 API Overview

This API provides comprehensive endpoints for:
- Todo list management (CRUD operations)
- Task management with ordering and toggling
- Shopping list functionality
- Real-time search capabilities
- Bulk operations for efficiency

All endpoints include proper error handling, validation, and comprehensive documentation.

## 🚀 Deployment

This API is deployed using Docker containers with automated CI/CD through GitHub Actions and Ansible.

### Production Environment

- **URL**: `http://YOUR_SERVER_IP:8000`
- **Health Check**: `GET /ping`
- **Documentation**: `GET /openapi`

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

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect() 