# Database session management 
import logging
from edgy import Database, Registry
from core.config import settings

logger = logging.getLogger(__name__)

# Create database instance with environment-aware configuration
try:
    database_url = settings.get_database_url()
    logger.info(f"Initializing database with URL: {database_url[:20]}...")
    database = Database(database_url)
    logger.info("Database instance created successfully")
except Exception as e:
    logger.error(f"Failed to create database instance: {type(e).__name__}: {e}", exc_info=True)
    raise

# Create a shared registry instance
try:
    # Avoid duplicate model registration during mixed app/migration imports
    models_registry = Registry(database=database, on_conflict="keep")
    logger.info("Models registry created successfully")
except Exception as e:
    logger.error(f"Failed to create models registry: {type(e).__name__}: {e}", exc_info=True)
    raise

# Note: Models will import models_registry directly to avoid circular imports
# and will be imported by application modules or migrations as needed.