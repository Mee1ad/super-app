# Database session management 
from edgy import Database, Registry
from core.config import settings

# Create database instance
database = Database(settings.database_url)

# Create a shared registry instance
models_registry = Registry(database=database)

# Import models to register them with the database
# This will be done after the registry is created
from apps.todo.models import List, Task, ShoppingItem 