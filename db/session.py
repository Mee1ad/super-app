# Database session management 
from edgy import Database
from core.config import settings

# Create database instance
database = Database(settings.database_url)

# Import models to register them
from apps.todo.models import List, Task, ShoppingItem 