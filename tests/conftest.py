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

# Configure pytest-asyncio
pytest_plugins = ["pytest_asyncio"]

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def anyio_backend():
    """Use asyncio backend for tests"""
    return "asyncio"

@pytest.fixture(scope="session", autouse=True)
def setup_test_database(event_loop):
    """Setup and teardown database for the entire test session"""
    async def setup():
        try:
            # Connect to database
            await database.connect()
            print(f"Connected to test database: {database.url}")
            
            # Create tables
            await models_registry.create_all()
            print("Created all tables for tests")
            
        except Exception as e:
            print(f"Database setup failed: {e}")
            raise

    async def teardown():
        try:
            # Clean up - drop all tables
            await models_registry.drop_all()
            print("Dropped all tables after tests")
        except Exception as e:
            print(f"Table cleanup failed: {e}")
        
        try:
            # Disconnect from database
            await database.disconnect()
            print("Disconnected from test database")
        except Exception as e:
            print(f"Database disconnect failed: {e}")

    # Run setup
    event_loop.run_until_complete(setup())
    
    yield
    
    # Run teardown
    event_loop.run_until_complete(teardown())

@pytest.fixture
def test_client():
    """Create a test client for the application"""
    return EsmeraldTestClient(app) 