"""
Migration Integration Tests
Integration tests for the migration system
"""
import pytest
import pytest_asyncio
import asyncio
import sys
import os
from unittest.mock import patch

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from db.migrate_incremental import main
from db.session import database
from core.config import settings


@pytest_asyncio.fixture
async def setup_test_environment():
    """Setup test environment for migration tests"""
    # Connect to database
    await database.connect()
    
    # Clean up any existing test data
    await database.execute("DELETE FROM migrations WHERE version LIKE '999%'")
    await database.execute("DROP TABLE IF EXISTS test_migration_table")
    
    yield
    
    # Clean up after tests
    await database.execute("DELETE FROM migrations WHERE version LIKE '999%'")
    await database.execute("DROP TABLE IF EXISTS test_migration_table")
    await database.disconnect()


class TestMigrationIntegration:
    """Integration tests for migration system"""
    
    @pytest.mark.asyncio
    async def test_migration_status_command(self, setup_test_environment):
        """Test migration status command"""
        with patch('sys.argv', ['migrate_incremental.py', 'status']):
            await main()
        
        # Verify migrations table exists
        result = await database.fetch_one("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'migrations'
        """)
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_migration_schema_fix_integration(self, setup_test_environment):
        """Test that schema fixes work in integration"""
        # Create a moods table with wrong schema
        await database.execute("""
            CREATE TABLE IF NOT EXISTS moods (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(100) NOT NULL,
                description TEXT
            )
        """)
        
        # Run migration status (this will trigger schema fix)
        with patch('sys.argv', ['migrate_incremental.py', 'status']):
            await main()
        
        # Check if schema was fixed
        desc_result = await database.fetch_one("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'moods' AND column_name = 'description'
        """)
        assert desc_result is None  # Description column should be removed
        
        emoji_result = await database.fetch_one("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'moods' AND column_name = 'emoji'
        """)
        assert emoji_result is not None  # Emoji column should exist
        
        # Clean up
        await database.execute("DROP TABLE IF EXISTS moods")
    
    @pytest.mark.asyncio
    async def test_migration_table_recreation_integration(self, setup_test_environment):
        """Test migration table recreation in integration"""
        # Drop and recreate migrations table with wrong schema
        await database.execute("DROP TABLE IF EXISTS migrations")
        await database.execute("""
            CREATE TABLE migrations (
                id SERIAL PRIMARY KEY,
                wrong_column VARCHAR(100)
            )
        """)
        
        # Run migration status (this should recreate the table)
        with patch('sys.argv', ['migrate_incremental.py', 'status']):
            await main()
        
        # Check if table was recreated with correct schema
        version_result = await database.fetch_one("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'migrations' AND column_name = 'version'
        """)
        assert version_result is not None
        
        wrong_result = await database.fetch_one("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'migrations' AND column_name = 'wrong_column'
        """)
        assert wrong_result is None


class TestMigrationErrorHandling:
    """Test migration error handling in integration"""
    
    @pytest.mark.asyncio
    async def test_migration_with_invalid_database_connection(self):
        """Test migration behavior with invalid database connection"""
        # Temporarily change database URL to invalid one
        original_url = settings.get_database_url()
        
        try:
            # This should fail gracefully
            with patch('core.config.settings.db_host', 'invalid-host'):
                with patch('sys.argv', ['migrate_incremental.py', 'status']):
                    # Should not raise exception, just log error
                    await main()
        finally:
            # Restore original settings
            pass
    
    @pytest.mark.asyncio
    async def test_migration_with_missing_migration_files(self, setup_test_environment):
        """Test migration behavior with missing migration files"""
        # This should work even if some migration files are missing
        with patch('sys.argv', ['migrate_incremental.py', 'status']):
            await main()
        
        # Should not crash, just log warnings about missing files 