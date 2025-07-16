"""
Migration Tests
Tests for the incremental migration system
"""
import pytest
import pytest_asyncio
import asyncio
from unittest.mock import patch, MagicMock

from db.migrations.base import MigrationManager, Migration
from db.session import database
from core.config import settings


class MockMigration(Migration):
    """Mock migration for testing"""
    
    def get_version(self) -> str:
        return "999"
    
    def get_name(self) -> str:
        return "test_migration"
    
    def get_description(self) -> str:
        return "Test migration for unit testing"
    
    def get_dependencies(self) -> list[str]:
        return []
    
    async def up(self) -> None:
        """Mock migration up"""
        await database.execute("CREATE TABLE IF NOT EXISTS test_table (id SERIAL PRIMARY KEY, name VARCHAR(100))")
    
    async def down(self) -> None:
        """Mock migration down"""
        await database.execute("DROP TABLE IF EXISTS test_table")


@pytest_asyncio.fixture
async def migration_manager():
    """Create a migration manager for testing"""
    manager = MigrationManager()
    yield manager


@pytest_asyncio.fixture
async def mock_migration():
    """Create a mock migration"""
    return MockMigration()


class TestMigrationManager:
    """Test the migration manager"""
    
    @pytest.mark.asyncio
    async def test_register_migration(self, migration_manager, mock_migration):
        """Test registering a migration"""
        migration_manager.register_migration(mock_migration)
        assert len(migration_manager.migrations) == 1
        assert migration_manager.migrations[0].version == "999"
    
    @pytest.mark.asyncio
    async def test_ensure_migration_table(self, migration_manager):
        """Test ensuring migration table exists"""
        await migration_manager.ensure_migration_table()
        
        # Check if table exists
        result = await database.fetch_one("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'migrations'
        """)
        assert result is not None
        
        # Check if table has correct schema
        columns = await database.fetch_all("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'migrations' 
            ORDER BY ordinal_position
        """)
        column_names = [row[0] for row in columns]
        
        expected_columns = ['id', 'version', 'name', 'description', 'dependencies', 'created_at', 'applied_at']
        for col in expected_columns:
            assert col in column_names
    
    @pytest.mark.asyncio
    async def test_fix_table_schemas(self, migration_manager):
        """Test fixing table schemas"""
        # Create a moods table with description column (wrong schema)
        await database.execute("""
            CREATE TABLE IF NOT EXISTS moods (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(100) NOT NULL,
                description TEXT
            )
        """)
        
        # Run schema fix
        await migration_manager.fix_table_schemas()
        
        # Check if description column was removed
        result = await database.fetch_one("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'moods' AND column_name = 'description'
        """)
        assert result is None
        
        # Check if emoji and color columns were added
        emoji_result = await database.fetch_one("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'moods' AND column_name = 'emoji'
        """)
        assert emoji_result is not None
        
        color_result = await database.fetch_one("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'moods' AND column_name = 'color'
        """)
        assert color_result is not None
        
        # Clean up
        await database.execute("DROP TABLE IF EXISTS moods")
    
    @pytest.mark.asyncio
    async def test_migration_lifecycle(self, migration_manager, mock_migration):
        """Test complete migration lifecycle"""
        # Register migration
        migration_manager.register_migration(mock_migration)
        
        # Ensure migration table exists
        await migration_manager.ensure_migration_table()
        
        # Check initial status
        applied_migrations = await migration_manager.get_applied_migrations()
        assert "999" not in applied_migrations
        
        # Run migration
        await migration_manager.migrate()
        
        # Check if migration was applied
        applied_migrations = await migration_manager.get_applied_migrations()
        assert "999" in applied_migrations
        
        # Check if test table was created
        result = await database.fetch_one("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'test_table'
        """)
        assert result is not None
        
        # Clean up
        await database.execute("DROP TABLE IF EXISTS test_table")
        await database.execute("DELETE FROM migrations WHERE version = '999'")


class TestMigrationSchema:
    """Test migration schema handling"""
    
    @pytest.mark.asyncio
    async def test_migration_table_recreation(self):
        """Test that migration table is recreated if schema is wrong"""
        manager = MigrationManager()
        
        # Create migration table with wrong schema
        await database.execute("DROP TABLE IF EXISTS migrations")
        await database.execute("""
            CREATE TABLE migrations (
                id SERIAL PRIMARY KEY,
                wrong_column VARCHAR(100)
            )
        """)
        
        # Ensure migration table (should recreate with correct schema)
        await manager.ensure_migration_table()
        
        # Check if table has correct schema
        result = await database.fetch_one("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'migrations' AND column_name = 'version'
        """)
        assert result is not None
        
        # Check if wrong column was removed
        wrong_result = await database.fetch_one("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'migrations' AND column_name = 'wrong_column'
        """)
        assert wrong_result is None


class TestMigrationDependencies:
    """Test migration dependency handling"""
    
    @pytest.mark.asyncio
    async def test_dependency_check(self, migration_manager):
        """Test dependency checking"""
        # Create migrations with dependencies
        class Migration001(Migration):
            def get_version(self) -> str: return "001"
            def get_name(self) -> str: return "first"
            def get_description(self) -> str: return "First migration"
            def get_dependencies(self) -> list[str]: return []
            async def up(self) -> None: pass
            async def down(self) -> None: pass
        
        class Migration002(Migration):
            def get_version(self) -> str: return "002"
            def get_name(self) -> str: return "second"
            def get_description(self) -> str: return "Second migration"
            def get_dependencies(self) -> list[str]: return ["001"]
            async def up(self) -> None: pass
            async def down(self) -> None: pass
        
        migration1 = Migration001()
        migration2 = Migration002()
        
        migration_manager.register_migration(migration1)
        migration_manager.register_migration(migration2)
        
        # Check dependencies before running migrations
        assert await migration_manager.check_dependencies(migration1) == True
        assert await migration_manager.check_dependencies(migration2) == False  # 001 not applied yet
        
        # Run migrations
        await migration_manager.ensure_migration_table()
        await migration_manager.migrate()
        
        # Check dependencies after running migrations
        assert await migration_manager.check_dependencies(migration2) == True  # 001 now applied 