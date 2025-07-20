# Backend Test Organization

This directory contains all backend tests organized by type and functionality.

## Directory Structure

```
tests/
├── unit/                    # Unit tests for individual components
│   ├── sentry/             # Sentry unit tests
│   ├── middleware/         # Middleware unit tests
│   ├── endpoints/          # Endpoint unit tests
│   ├── test_exceptions.py  # Exception handling tests
│   ├── test_schemas.py     # Schema validation tests
│   ├── test_models.py      # Database model tests
│   └── test_error_schemas.py # Error schema tests
├── integration/            # Integration tests
│   ├── sentry/            # Sentry integration tests
│   │   ├── test_sentry_integration.py
│   │   ├── test_sentry_message.py
│   │   ├── test_sentry_direct.py
│   │   ├── test_sentry_working.py
│   │   └── test_sentry_production.py
│   ├── middleware/        # Middleware integration tests
│   │   ├── test_middleware_working.py
│   │   ├── test_middleware_logging.py
│   │   └── test_middleware_config.py
│   ├── endpoints/         # Endpoint integration tests
│   │   ├── test_error_capture.py
│   │   ├── test_error_capture_fix.py
│   │   ├── test_unhandled_issues.py
│   │   ├── test_normal_endpoint.py
│   │   └── test_comprehensive_error_capture.py
│   ├── test_todo_endpoints.py
│   ├── test_migration_integration.py
│   └── test_postgresql_migrations.py
├── e2e/                   # End-to-end tests
├── performance/           # Performance tests
├── debug/                 # Debug and utility tests
│   ├── test_live_endpoint.py
│   ├── test_server_start.py
│   ├── test_decorator.py
│   ├── test_direct_exception.py
│   ├── test_simple_error.py
│   ├── test_exception_handler.py
│   ├── test_ping_error.py
│   └── test_sentry_current.py
├── conftest.py           # Pytest configuration
└── test_cors.py          # CORS tests
```

## Test Categories

### Unit Tests (`tests/unit/`)
- **Purpose**: Test individual components in isolation
- **Scope**: Single functions, classes, or modules
- **Dependencies**: Mocked external dependencies
- **Speed**: Fast execution

#### Sentry Unit Tests (`tests/unit/sentry/`)
- Test Sentry utility functions
- Test Sentry configuration
- Test error capture functions
- Test context setting functions

#### Middleware Unit Tests (`tests/unit/middleware/`)
- Test middleware functionality
- Test error handling in middleware
- Test request/response processing

#### Endpoint Unit Tests (`tests/unit/endpoints/`)
- Test individual endpoint functions
- Test request validation
- Test response formatting

### Integration Tests (`tests/integration/`)
- **Purpose**: Test component interactions
- **Scope**: Multiple components working together
- **Dependencies**: Real or test databases, external services
- **Speed**: Medium execution time

#### Sentry Integration Tests (`tests/integration/sentry/`)
- Test Sentry with real HTTP requests
- Test error capture in live scenarios
- Test Sentry configuration in different environments
- Test before_send_filter functionality

#### Middleware Integration Tests (`tests/integration/middleware/`)
- Test middleware with real requests
- Test error flow through middleware
- Test logging and debugging output
- Test middleware configuration

#### Endpoint Integration Tests (`tests/integration/endpoints/`)
- Test endpoints with real HTTP requests
- Test error handling in endpoints
- Test normal vs error scenarios
- Test comprehensive error capture

### End-to-End Tests (`tests/e2e/`)
- **Purpose**: Test complete user workflows
- **Scope**: Full application stack
- **Dependencies**: Complete test environment
- **Speed**: Slow execution

### Performance Tests (`tests/performance/`)
- **Purpose**: Test application performance
- **Scope**: Load testing, stress testing
- **Dependencies**: Performance monitoring tools
- **Speed**: Variable execution time

### Debug Tests (`tests/debug/`)
- **Purpose**: Debugging and troubleshooting
- **Scope**: Specific issues or scenarios
- **Dependencies**: Debug configurations
- **Speed**: Variable execution time

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Sentry tests only
pytest tests/unit/sentry/ tests/integration/sentry/

# Middleware tests only
pytest tests/unit/middleware/ tests/integration/middleware/

# Endpoint tests only
pytest tests/unit/endpoints/ tests/integration/endpoints/
```

### Run Specific Test Files
```bash
# Run specific test file
pytest tests/integration/sentry/test_sentry_integration.py

# Run with verbose output
pytest tests/integration/sentry/test_sentry_integration.py -v

# Run with coverage
pytest tests/integration/sentry/test_sentry_integration.py --cov=core.sentry
```

### Debug Tests
```bash
# Run debug tests
pytest tests/debug/

# Run with print statements
pytest tests/debug/ -s

# Run specific debug test
pytest tests/debug/test_sentry_current.py -s
```

## Test Naming Conventions

### File Naming
- `test_*.py` - Test files
- `conftest.py` - Pytest configuration
- `README.md` - Documentation

### Test Function Naming
- `test_*` - Test functions
- `test_*_success` - Success scenario tests
- `test_*_error` - Error scenario tests
- `test_*_integration` - Integration tests
- `test_*_unit` - Unit tests

### Class Naming
- `Test*` - Test classes
- `Test*Integration` - Integration test classes
- `Test*Unit` - Unit test classes

## Test Organization Principles

1. **Separation of Concerns**: Each test type has its own directory
2. **Clear Naming**: Test names clearly indicate what they test
3. **Proper Scope**: Tests are scoped appropriately (unit vs integration)
4. **Maintainability**: Tests are easy to find and maintain
5. **Documentation**: Each test directory has clear documentation

## Best Practices

1. **Unit Tests**: Should be fast and isolated
2. **Integration Tests**: Should test real interactions
3. **E2E Tests**: Should test complete workflows
4. **Debug Tests**: Should help with troubleshooting
5. **Performance Tests**: Should measure actual performance

## Adding New Tests

1. **Choose the right category**: Unit, integration, e2e, performance, or debug
2. **Follow naming conventions**: Use clear, descriptive names
3. **Add to appropriate directory**: Place in the correct subdirectory
4. **Update documentation**: Update this README if needed
5. **Run tests**: Ensure all tests pass before committing 