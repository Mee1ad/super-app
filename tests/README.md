# Testing Strategy

This project implements a **hybrid testing strategy** that combines fast SQLite unit tests with comprehensive PostgreSQL integration tests.

## Testing Architecture

### 1. SQLite Unit Tests (Fast Feedback)
- **Location**: `tests/unit/`
- **Database**: SQLite (in-memory/file-based)
- **Purpose**: Fast unit tests for business logic, models, and basic migrations
- **Benefits**: 
  - Rapid feedback during development
  - No external dependencies
  - Fast execution in CI/CD
  - Isolated test environment

### 2. PostgreSQL Integration Tests (Production Parity)
- **Location**: `tests/integration/`
- **Database**: PostgreSQL (service container in CI)
- **Purpose**: Integration tests for PostgreSQL-specific features and real-world scenarios
- **Benefits**:
  - Tests actual production database system
  - Validates PostgreSQL-specific features
  - Catches database-specific issues
  - Ensures migration compatibility

## Test Categories

### Unit Tests (SQLite)
- `tests/unit/test_migrations.py` - Migration system unit tests
- `tests/unit/test_models.py` - Database model tests
- `tests/unit/test_schemas.py` - Pydantic schema tests
- `tests/unit/test_error_schemas.py` - Error handling tests

### Integration Tests (PostgreSQL)
- `tests/integration/test_migration_integration.py` - Migration integration tests
- `tests/integration/test_postgresql_migrations.py` - PostgreSQL-specific migration tests
- `tests/integration/test_todo_endpoints.py` - API endpoint integration tests

### Specialized Tests
- `tests/test_cors.py` - CORS configuration tests

## Running Tests

### Local Development

#### SQLite Tests (Fast)
```bash
# Run all unit tests with SQLite
pytest tests/unit/ -v

# Run specific test file
pytest tests/unit/test_migrations.py -v

# Run with coverage
pytest tests/unit/ --cov=apps --cov=db --cov=core --cov-report=term-missing
```

#### PostgreSQL Tests (Comprehensive)
```bash
# Option 1: Use the setup script (Recommended)
./scripts/setup-test-db.sh

# Option 2: Manual setup
# Ensure PostgreSQL is running locally
# Set environment variables for PostgreSQL testing
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=test_db
export DB_USER=postgres
export DB_PASSWORD=postgres
export ENVIRONMENT=test

# Run PostgreSQL integration tests
pytest tests/integration/ -v

# Run PostgreSQL-specific migration tests
pytest tests/integration/test_postgresql_migrations.py -v
```

#### All Tests
```bash
# Run all tests (both SQLite and PostgreSQL)
pytest tests/ -v
```

### CI/CD Pipeline

The GitHub Actions workflow automatically runs:

1. **SQLite Tests** (`test-sqlite` job):
   - Unit tests with SQLite
   - CORS tests
   - Migration unit tests

2. **PostgreSQL Tests** (`test-postgresql` job):
   - Integration tests with PostgreSQL service container
   - Migration integration tests
   - PostgreSQL-specific feature tests

3. **Deployment** (`deploy` job):
   - Only runs after both test jobs pass
   - Deploys to production server

## Test Configuration

### Environment Variables

#### SQLite Testing (Default)
- No specific environment variables needed
- Uses `sqlite:///./test.db` automatically

#### PostgreSQL Testing
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=test_db
DB_USER=postgres
DB_PASSWORD=postgres
ENVIRONMENT=test
```

### Test Fixtures

#### SQLite Configuration
```python
@pytest.fixture
def sqlite_test_config():
    """Configure for SQLite testing"""
    # Clears PostgreSQL environment variables
    # Uses default SQLite configuration
```

#### PostgreSQL Configuration
```python
@pytest.fixture
def postgresql_test_config():
    """Configure for PostgreSQL testing"""
    # Sets PostgreSQL environment variables
    # Uses PostgreSQL service container
```

## PostgreSQL-Specific Features Tested

### 1. Data Types
- UUID with `gen_random_uuid()`
- JSON/JSONB columns
- ARRAY types
- TIMESTAMP WITH TIME ZONE

### 2. Advanced Features
- Full-text search with `tsvector`
- Generated columns
- Advanced indexing
- Constraint validation

### 3. Migration Features
- Extension management (`uuid-ossp`)
- Schema validation
- Rollback operations
- Connection pooling

## Best Practices

### 1. Test Isolation
- Each test should be independent
- Use fixtures for setup/teardown
- Clean up test data after each test

### 2. Database Cleanup
```python
@pytest_asyncio.fixture
async def clean_database():
    """Clean database fixture for tests"""
    await database.connect()
    # Clean up test data
    yield
    # Clean up after tests
    await database.disconnect()
```

### 3. Environment Configuration
- Use environment variables for database configuration
- Test both SQLite and PostgreSQL paths
- Validate configuration in tests

### 4. Error Handling
- Test both success and failure scenarios
- Validate error messages and status codes
- Test constraint violations

## Database Setup

### Quick Setup

#### Windows
```powershell
# Run the setup script
.\scripts\setup-test-db.ps1

# Or with verbose output
.\scripts\setup-test-db.ps1 -Verbose
```

#### Linux/macOS
```bash
# Make script executable (first time only)
chmod +x scripts/setup-test-db.sh

# Run the setup script
./scripts/setup-test-db.sh

# Or with verbose output
./scripts/setup-test-db.sh --verbose
```

### Manual Setup

#### 1. Install PostgreSQL
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows (using Chocolatey)
choco install postgresql
```

#### 2. Start PostgreSQL Service
```bash
# Ubuntu/Debian
sudo systemctl start postgresql

# macOS
brew services start postgresql

# Windows
net start postgresql
```

#### 3. Create Test Database
```bash
# Connect to PostgreSQL
psql -U postgres

# Create test database
CREATE DATABASE test_db;

# Exit
\q
```

#### 4. Set Environment Variables
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=test_db
export DB_USER=postgres
export DB_PASSWORD=postgres
export ENVIRONMENT=test
```

## Troubleshooting

### Common Issues

#### PostgreSQL Connection Issues
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check connection
psql -h localhost -p 5432 -U postgres -d test_db
```

#### Test Environment Issues
```bash
# Clear test database
rm -f test.db

# Reset environment variables
unset DB_HOST DB_NAME DB_USER DB_PASSWORD DB_PORT
```

#### CI/CD Issues
- Check PostgreSQL service container logs
- Verify environment variables are set
- Ensure database is ready before running tests

### Debugging Tests

#### Verbose Output
```bash
pytest tests/ -v -s --tb=long
```

#### Database Debugging
```python
# Add to test for debugging
print(f"Database URL: {settings.get_database_url()}")
print(f"Environment: {settings.environment}")
```

## Migration Testing Strategy

### 1. Unit Tests (SQLite)
- Test migration logic and dependencies
- Validate migration manager functionality
- Test schema fixes and table recreation

### 2. Integration Tests (PostgreSQL)
- Test actual migration execution
- Validate PostgreSQL-specific features
- Test rollback operations
- Verify data integrity

### 3. Production Parity
- Use same PostgreSQL version as production
- Test with production-like data
- Validate performance characteristics

This hybrid approach ensures both fast development feedback and comprehensive production validation. 