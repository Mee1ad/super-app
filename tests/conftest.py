import pytest
import asyncio
import sys
from esmerald.testclient import EsmeraldTestClient
from main import app
from db.session import database, models_registry

# Import all models to ensure they are registered with the registry
from apps.todo.models import List, Task, ShoppingItem

# Fix Windows event loop issue
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

pytest_plugins = ["pytest_asyncio"]
pytestmark = pytest.mark.asyncio

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def setup_database():
    """Setup and teardown database for the entire test session"""
    # Connect to database
    await database.connect()
    
    # Create tables
    await models_registry.create_all()
    
    yield
    
    # Clean up - drop all tables
    await models_registry.drop_all()
    
    # Disconnect from database
    await database.disconnect()

@pytest.fixture
def test_client():
    """Create a test client for the application"""
    return EsmeraldTestClient(app) 