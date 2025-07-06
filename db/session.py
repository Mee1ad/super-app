# Database session management 
from edgy import Database
from core.config import settings

# Create database instance
database = Database(settings.database_url)

# Import models to register them with the database
from apps.todo.models import List, Task, ShoppingItem

# Ensure models are registered with the database
List.Meta.database = database
Task.Meta.database = database
ShoppingItem.Meta.database = database 