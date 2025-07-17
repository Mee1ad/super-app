"""
Test configuration and fixtures
"""
import pytest
import pytest_asyncio
import asyncio
import os
import sys
from unittest.mock import patch

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.session import database
from core.config import settings


@pytest_asyncio.fixture
async def database_connection():
    """Database connection fixture"""
    await database.connect()
    yield database
    await database.disconnect()


@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    with patch('core.config.settings') as mock:
        mock.environment = "test"
        mock.is_testing = True
        mock.debug = True
        yield mock


@pytest.fixture
def sqlite_test_config():
    """Configure for SQLite testing"""
    # Clear any PostgreSQL environment variables
    original_env = {}
    for key in ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_PORT']:
        if key in os.environ:
            original_env[key] = os.environ[key]
            del os.environ[key]
    
    yield
    
    # Restore original environment
    for key, value in original_env.items():
        os.environ[key] = value


@pytest.fixture
def postgresql_test_config():
    """Configure for PostgreSQL testing"""
    # Set PostgreSQL environment variables
    original_env = {}
    for key in ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_PORT']:
        if key in os.environ:
            original_env[key] = os.environ[key]
    
    # Set PostgreSQL test configuration
    os.environ.update({
        'DB_HOST': 'localhost',
        'DB_PORT': '5432',
        'DB_NAME': 'test_db',
        'DB_USER': 'postgres',
        'DB_PASSWORD': 'postgres',
        'ENVIRONMENT': 'test'
    })
    
    yield
    
    # Restore original environment
    for key, value in original_env.items():
        os.environ[key] = value
    else:
        # Remove test environment variables if they didn't exist before
        for key in ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_PORT']:
            if key in os.environ:
                del os.environ[key]


@pytest_asyncio.fixture
async def clean_database():
    """Clean database fixture for tests"""
    await database.connect()
    
    # Clean up test data
    await database.execute("DELETE FROM migrations WHERE version LIKE '999%'")
    
    # Drop test tables
    test_tables = [
        'test_table', 'test_migration_table', 'test_postgresql_table',
        'test_json_table', 'test_search_table', 'test_index_table',
        'test_constraints_table', 'test_uuid_table', 'test_timestamp_table',
        'test_array_table'
    ]
    
    for table in test_tables:
        await database.execute(f"DROP TABLE IF EXISTS {table}")
    
    yield
    
    # Clean up after tests
    await database.execute("DELETE FROM migrations WHERE version LIKE '999%'")
    for table in test_tables:
        await database.execute(f"DROP TABLE IF EXISTS {table}")
    
    await database.disconnect()


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session"""
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Mark all async tests
pytestmark = pytest.mark.asyncio 