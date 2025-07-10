# Environment Configuration Guide

This guide explains how to differentiate local and production database configurations in the super-app-backend project.

## Overview

The application supports multiple environments (development, production, test) with different database configurations. This is achieved through environment variables and configuration files.

## Configuration Methods

### 1. Environment Variables (Recommended)

The application uses `pydantic-settings` to load configuration from environment variables with fallbacks.

**Priority Order:**
1. Environment variables (highest priority)
2. `.env` file
3. Default values in code (lowest priority)

### 2. Configuration Files

- **`.env`** - Local development (gitignored)
- **`.envrc`** - Development environment variables (gitignored)
- **`env.production`** - Production settings (gitignored)
- **`env.example`** - Template for environment setup

### 3. GitHub Secrets (CI/CD)

Used in GitHub Actions for automated deployment:
- `DB_PASSWORD` - Production database password
- `API_KEY` - Production API key
- `SSH_PRIVATE_KEY` - Server access key

### 4. Docker Secrets (Production)

Used in Docker Compose for containerized deployment:
- `/run/secrets/api_key` - API authentication
- `/run/secrets/db_password` - Database password

## Environment Setup

### Development Environment

**Method 1: Using PowerShell Script (Windows)**
```powershell
.\scripts\setup-env.ps1 dev
```

**Method 2: Using Bash Script (Linux/WSL)**
```bash
./scripts/setup-env.sh dev
```

**Method 3: Manual Setup**
```bash
# Create .env file with actual development values
cat > .env << 'EOF'
ENVIRONMENT=development
DATABASE_URL=postgresql://postgres:admin@localhost:5432/lifehub
DEBUG=true
EOF

# Or set environment variables directly
export ENVIRONMENT="development"
export DATABASE_URL="postgresql://postgres:admin@localhost:5432/lifehub"
export DEBUG="true"
```

### Production Environment

**Method 1: Using PowerShell Script**
```powershell
.\scripts\setup-env.ps1 production
```

**Method 2: Manual Setup**
```bash
# Create production environment file with actual production values
cat > env.production << 'EOF'
ENVIRONMENT=production
DATABASE_URL=postgresql://superapp:superapp123@65.108.157.187:5432/superapp
SECRET_KEY=your-production-secret-key-here
API_KEY=your-production-api-key-here
DEBUG=false
EOF

# Load production environment
source env.production
```

**Method 3: Direct Environment Variables**
```bash
export ENVIRONMENT="production"
export DATABASE_URL="postgresql://superapp:superapp123@65.108.157.187:5432/superapp"
export DEBUG="false"
```

## Database Configuration

### Development Database
- **Host**: `localhost`
- **Port**: `5432`
- **Database**: `lifehub`
- **Username**: `postgres`
- **Password**: `admin`
- **URL**: `postgresql://postgres:admin@localhost:5432/lifehub`

### Production Database
- **Host**: `65.108.157.187`
- **Port**: `5432`
- **Database**: `superapp`
- **Username**: `superapp`
- **Password**: `superapp123`
- **URL**: `postgresql://superapp:superapp123@65.108.157.187:5432/superapp`

### Test Database
- **Host**: `localhost`
- **Port**: `5432`
- **Database**: `lifehub_test`
- **Username**: `postgres`
- **Password**: `admin`
- **URL**: `postgresql://postgres:admin@localhost:5432/lifehub_test`

## Configuration Files Structure

### env.example
```bash
# Environment Configuration
ENVIRONMENT=development

# Development Database (local) - Replace with your actual values
DATABASE_URL=postgresql://username:password@localhost:5432/database_name

# Production Database (remote) - Replace with your actual values
PROD_DATABASE_HOST=your_production_host
PROD_DATABASE_PORT=5432
PROD_DATABASE_NAME=your_production_database
PROD_DATABASE_USER=your_production_user
PROD_DATABASE_PASSWORD=your_production_password

# Security - Replace with your actual values
SECRET_KEY=your-secret-key-here
API_KEY=your-api-key-here
DEBUG=true
```

### .envrc (Development)
```bash
# Environment
export ENVIRONMENT="development"

# Development Database
export DATABASE_URL="postgresql://postgres:admin@localhost:5432/lifehub"

# Production Database (for reference)
export PROD_DATABASE_HOST="65.108.157.187"
export PROD_DATABASE_PORT="5432"
export PROD_DATABASE_NAME="superapp"
export PROD_DATABASE_USER="superapp"
export PROD_DATABASE_PASSWORD="superapp123"
```

### env.production
```bash
# Production Environment Configuration
ENVIRONMENT=production
DATABASE_URL=postgresql://superapp:superapp123@65.108.157.187:5432/superapp
SECRET_KEY=your-production-secret-key-here
API_KEY=your-production-api-key-here
DEBUG=false
```

## Code Implementation

### core/config.py
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # Database Configuration
    database_url: str = "postgresql://postgres:admin@localhost:5432/lifehub"
    
    # Production Database (fallback)
    prod_database_host: str = "65.108.157.187"
    prod_database_port: int = 5432
    prod_database_name: str = "superapp"
    prod_database_user: str = "superapp"
    prod_database_password: str = "superapp123"
    
    @property
    def is_production(self) -> bool:
        return self.environment.lower() in ["production", "prod"]
    
    @property
    def is_development(self) -> bool:
        return self.environment.lower() in ["development", "dev", "local"]
    
    def get_database_url(self) -> str:
        if self.is_production:
            return f"postgresql://{self.prod_database_user}:{self.prod_database_password}@{self.prod_database_host}:{self.prod_database_port}/{self.prod_database_name}"
        else:
            return self.database_url

settings = Settings()
```

### db/session.py
```python
from edgy import Database, Registry
from core.config import settings

# Create database instance with environment-aware configuration
database = Database(settings.get_database_url())
models_registry = Registry(database=database)
```

## Security Best Practices

### ✅ Do:
- Use environment variables for sensitive data
- Keep production credentials in gitignored files
- Use different databases for different environments
- Use strong, unique passwords in production
- Use GitHub Secrets for CI/CD
- Use Docker Secrets for containerized deployment

### ❌ Don't:
- Commit sensitive data to version control
- Use the same credentials across environments
- Use weak passwords in production
- Hardcode database credentials in code
- Share production credentials in plain text

## Environment Detection

The application automatically detects the environment and uses the appropriate configuration:

```python
# Check current environment
if settings.is_production:
    print("Running in production mode")
elif settings.is_development:
    print("Running in development mode")

# Get appropriate database URL
db_url = settings.get_database_url()
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check if PostgreSQL is running
   - Verify database credentials
   - Ensure database exists

2. **Environment Variables Not Loading**
   - Check if `.env` file exists
   - Verify environment variable names
   - Restart your terminal/IDE

3. **Production Environment Not Working**
   - Ensure `env.production` file exists
   - Check if file is properly formatted
   - Verify all required variables are set

### Validation Commands

```bash
# Test environment setup
.\scripts\setup-env.ps1 dev

# Test database connection
python -c "from db.session import database; print('Database configured:', database.url)"

# Check environment variables
echo $ENVIRONMENT
echo $DATABASE_URL
```

## Migration Guide

### From Old Configuration

If you're migrating from the old configuration:

1. **Update core/config.py** - Use the new environment-aware configuration
2. **Create environment files** - Set up `.env`, `env.production` as needed
3. **Update database session** - Use `settings.get_database_url()`
4. **Test environments** - Verify both development and production work

### Example Migration

**Old way:**
```python
database_url: str = "postgresql://postgres:admin@localhost:5432/lifehub"
```

**New way:**
```python
def get_database_url(self) -> str:
    if self.is_production:
        return f"postgresql://{self.prod_database_user}:{self.prod_database_password}@{self.prod_database_host}:{self.prod_database_port}/{self.prod_database_name}"
    else:
        return self.database_url
```

## Summary

This configuration system provides:

- **Flexibility**: Easy switching between environments
- **Security**: Sensitive data kept out of version control
- **Automation**: Scripts for easy environment setup
- **Validation**: Built-in environment validation
- **Scalability**: Easy to add new environments (staging, testing)

Choose the method that best fits your workflow and security requirements. 