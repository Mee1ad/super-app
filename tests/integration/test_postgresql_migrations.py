"""
PostgreSQL-specific Migration Tests
Integration tests for PostgreSQL-specific migration features
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
async def setup_postgresql_test_environment(postgresql_test_config):
    """Setup PostgreSQL test environment for migration tests"""
    # Connect to database
    await database.connect()
    
    # Clean up any existing test data
    await database.execute("DELETE FROM migrations WHERE version LIKE '999%'")
    await database.execute("DROP TABLE IF EXISTS test_postgresql_table")
    await database.execute("DROP TABLE IF EXISTS test_json_table")
    
    yield
    
    # Clean up after tests
    await database.execute("DELETE FROM migrations WHERE version LIKE '999%'")
    await database.execute("DROP TABLE IF EXISTS test_postgresql_table")
    await database.execute("DROP TABLE IF EXISTS test_json_table")
    await database.disconnect()


class TestPostgreSQLSpecificMigrations:
    """PostgreSQL-specific migration tests"""
    
    @pytest.mark.asyncio
    async def test_postgresql_uuid_extension(self, setup_postgresql_test_environment):
        """Test that UUID extension is available in PostgreSQL"""
        # Check if uuid-ossp extension is available
        result = await database.fetch_one("""
            SELECT extname FROM pg_extension WHERE extname = 'uuid-ossp'
        """)
        
        if result is None:
            # Try to create the extension
            try:
                await database.execute("CREATE EXTENSION IF NOT EXISTS uuid-ossp")
                result = await database.fetch_one("""
                    SELECT extname FROM pg_extension WHERE extname = 'uuid-ossp'
                """)
            except Exception as e:
                pytest.skip(f"UUID extension not available: {e}")
        
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_postgresql_json_operations(self, setup_postgresql_test_environment):
        """Test PostgreSQL JSON operations"""
        # Create a table with JSON column
        await database.execute("""
            CREATE TABLE test_json_table (
                id SERIAL PRIMARY KEY,
                data JSONB,
                metadata JSON
            )
        """)
        
        # Test JSON operations
        await database.execute("""
            INSERT INTO test_json_table (data, metadata) 
            VALUES ('{"key": "value", "nested": {"array": [1, 2, 3]}}', '{"type": "test"}')
        """)
        
        # Test JSON querying
        result = await database.fetch_one("""
            SELECT data->>'key' as key_value, 
                   data->'nested'->'array' as nested_array
            FROM test_json_table 
            WHERE id = 1
        """)
        
        assert result is not None
        assert result[0] == "value"  # key_value
        assert result[1] == '[1, 2, 3]'  # nested_array
    
    @pytest.mark.asyncio
    async def test_postgresql_full_text_search(self, setup_postgresql_test_environment):
        """Test PostgreSQL full-text search capabilities"""
        # Create a table with text search
        await database.execute("""
            CREATE TABLE test_search_table (
                id SERIAL PRIMARY KEY,
                title TEXT,
                content TEXT,
                search_vector tsvector GENERATED ALWAYS AS (
                    to_tsvector('english', title || ' ' || content)
                ) STORED
            )
        """)
        
        # Insert test data
        await database.execute("""
            INSERT INTO test_search_table (title, content) 
            VALUES ('PostgreSQL Guide', 'This is a comprehensive guide to PostgreSQL features')
        """)
        
        # Test full-text search
        result = await database.fetch_one("""
            SELECT title, content 
            FROM test_search_table 
            WHERE search_vector @@ to_tsquery('english', 'guide & features')
        """)
        
        assert result is not None
        assert "PostgreSQL Guide" in result[0]
    
    @pytest.mark.asyncio
    async def test_postgresql_indexes(self, setup_postgresql_test_environment):
        """Test PostgreSQL index creation and usage"""
        # Create a table with indexes
        await database.execute("""
            CREATE TABLE test_index_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        await database.execute("CREATE INDEX idx_test_index_name ON test_index_table(name)")
        await database.execute("CREATE INDEX idx_test_index_email ON test_index_table(email)")
        await database.execute("CREATE INDEX idx_test_index_created_at ON test_index_table(created_at)")
        
        # Insert test data
        await database.execute("""
            INSERT INTO test_index_table (name, email) 
            VALUES ('Test User', 'test@example.com')
        """)
        
        # Test index usage with EXPLAIN
        result = await database.fetch_one("""
            EXPLAIN (ANALYZE, BUFFERS) 
            SELECT * FROM test_index_table WHERE name = 'Test User'
        """)
        
        assert result is not None
        # Check if index was used (should contain "Index Scan" in the plan)
        plan_text = str(result[0])
        assert "Index Scan" in plan_text or "Bitmap Index Scan" in plan_text
    
    @pytest.mark.asyncio
    async def test_postgresql_constraints(self, setup_postgresql_test_environment):
        """Test PostgreSQL constraint handling"""
        # Create a table with various constraints
        await database.execute("""
            CREATE TABLE test_constraints_table (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                age INTEGER CHECK (age >= 0 AND age <= 150),
                status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'pending'))
            )
        """)
        
        # Test valid insert
        await database.execute("""
            INSERT INTO test_constraints_table (email, age, status) 
            VALUES ('test@example.com', 25, 'active')
        """)
        
        # Test constraint violations
        with pytest.raises(Exception):  # Should fail due to unique constraint
            await database.execute("""
                INSERT INTO test_constraints_table (email, age, status) 
                VALUES ('test@example.com', 30, 'active')
            """)
        
        with pytest.raises(Exception):  # Should fail due to check constraint
            await database.execute("""
                INSERT INTO test_constraints_table (email, age, status) 
                VALUES ('test2@example.com', -5, 'active')
            """)
        
        with pytest.raises(Exception):  # Should fail due to status check
            await database.execute("""
                INSERT INTO test_constraints_table (email, age, status) 
                VALUES ('test3@example.com', 30, 'invalid')
            """)
    
    @pytest.mark.asyncio
    async def test_postgresql_migration_rollback(self, setup_postgresql_test_environment):
        """Test PostgreSQL migration rollback functionality"""
        # Create a test migration table
        await database.execute("""
            CREATE TABLE test_migration_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert test data
        await database.execute("""
            INSERT INTO test_migration_table (name) VALUES ('Test Migration')
        """)
        
        # Verify data exists
        result = await database.fetch_one("""
            SELECT COUNT(*) FROM test_migration_table
        """)
        assert result[0] == 1
        
        # Test rollback (drop table)
        await database.execute("DROP TABLE test_migration_table")
        
        # Verify table is gone
        result = await database.fetch_one("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'test_migration_table'
            )
        """)
        assert result[0] is False
    
    @pytest.mark.asyncio
    async def test_postgresql_connection_pooling(self, setup_postgresql_test_environment):
        """Test PostgreSQL connection handling"""
        # Test multiple concurrent operations
        async def test_operation(operation_id):
            await database.execute("""
                INSERT INTO test_postgresql_table (name, operation_id) 
                VALUES ($1, $2)
            """, f"Operation {operation_id}", operation_id)
            
            result = await database.fetch_one("""
                SELECT name FROM test_postgresql_table 
                WHERE operation_id = $1
            """, operation_id)
            
            return result[0] if result else None
        
        # Create test table
        await database.execute("""
            CREATE TABLE test_postgresql_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                operation_id INTEGER
            )
        """)
        
        # Run concurrent operations
        tasks = [test_operation(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        # Verify all operations completed
        assert len(results) == 5
        assert all(result is not None for result in results)
        
        # Verify all records were inserted
        count_result = await database.fetch_one("""
            SELECT COUNT(*) FROM test_postgresql_table
        """)
        assert count_result[0] == 5


class TestPostgreSQLMigrationCompatibility:
    """Test PostgreSQL compatibility with existing migrations"""
    
    @pytest.mark.asyncio
    async def test_existing_migrations_with_postgresql(self, setup_postgresql_test_environment):
        """Test that existing migrations work with PostgreSQL"""
        # Run migration status to ensure compatibility
        with patch('sys.argv', ['migrate_incremental.py', 'status']):
            await main()
        
        # Verify migrations table exists with correct schema
        result = await database.fetch_one("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'migrations' 
            ORDER BY ordinal_position
        """)
        
        assert result is not None
        
        # Check for essential columns
        columns = await database.fetch_all("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'migrations' 
            ORDER BY ordinal_position
        """)
        
        column_names = [row[0] for row in columns]
        essential_columns = ['id', 'version', 'name', 'description', 'dependencies', 'created_at', 'applied_at']
        
        for col in essential_columns:
            assert col in column_names, f"Missing essential column: {col}"
    
    @pytest.mark.asyncio
    async def test_postgresql_specific_data_types(self, setup_postgresql_test_environment):
        """Test PostgreSQL-specific data types in migrations"""
        # Test UUID type
        await database.execute("""
            CREATE TABLE test_uuid_table (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(100)
            )
        """)
        
        # Test TIMESTAMP WITH TIME ZONE
        await database.execute("""
            CREATE TABLE test_timestamp_table (
                id SERIAL PRIMARY KEY,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Test ARRAY type
        await database.execute("""
            CREATE TABLE test_array_table (
                id SERIAL PRIMARY KEY,
                tags TEXT[],
                numbers INTEGER[]
            )
        """)
        
        # Insert test data
        await database.execute("""
            INSERT INTO test_uuid_table (name) VALUES ('Test UUID')
        """)
        
        await database.execute("""
            INSERT INTO test_timestamp_table DEFAULT VALUES
        """)
        
        await database.execute("""
            INSERT INTO test_array_table (tags, numbers) 
            VALUES (ARRAY['tag1', 'tag2'], ARRAY[1, 2, 3])
        """)
        
        # Verify data
        uuid_result = await database.fetch_one("SELECT COUNT(*) FROM test_uuid_table")
        timestamp_result = await database.fetch_one("SELECT COUNT(*) FROM test_timestamp_table")
        array_result = await database.fetch_one("SELECT COUNT(*) FROM test_array_table")
        
        assert uuid_result[0] == 1
        assert timestamp_result[0] == 1
        assert array_result[0] == 1
        
        # Clean up
        await database.execute("DROP TABLE test_uuid_table")
        await database.execute("DROP TABLE test_timestamp_table")
        await database.execute("DROP TABLE test_array_table") 