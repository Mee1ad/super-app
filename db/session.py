# Database session management 
from edgy import Database, Registry
from core.config import settings

# Create database instance with environment-aware configuration
database = Database(settings.get_database_url())

# Create a shared registry instance
models_registry = Registry(database=database)

# Note: Models will import models_registry directly to avoid circular imports 