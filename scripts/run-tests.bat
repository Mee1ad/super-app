@echo off
REM Hybrid Testing Script for Windows
REM Runs both SQLite unit tests and PostgreSQL integration tests

setlocal enabledelayedexpansion

REM Parse command line arguments
set SQLITE_ONLY=false
set POSTGRES_ONLY=false
set ALL_TESTS=false
set COVERAGE=false
set VERBOSE=false

:parse_args
if "%~1"=="" goto :end_parse
if "%~1"=="--sqlite-only" set SQLITE_ONLY=true
if "%~1"=="--postgres-only" set POSTGRES_ONLY=true
if "%~1"=="--all-tests" set ALL_TESTS=true
if "%~1"=="--coverage" set COVERAGE=true
if "%~1"=="--verbose" set VERBOSE=true
shift
goto :parse_args
:end_parse

REM Default to all tests if no specific option is provided
if "%SQLITE_ONLY%"=="false" if "%POSTGRES_ONLY%"=="false" if "%ALL_TESTS%"=="false" set ALL_TESTS=true

echo 🧪 Hybrid Testing Strategy
echo =========================

REM Build pytest arguments
set PYTEST_ARGS=-v
if "%VERBOSE%"=="true" set PYTEST_ARGS=-v -s
if "%COVERAGE%"=="true" set PYTEST_ARGS=%PYTEST_ARGS% --cov=apps --cov=db --cov=core --cov-report=term-missing

REM Function to run SQLite tests
:run_sqlite_tests
echo.
echo 🔵 Running SQLite Unit Tests...

REM Clear any PostgreSQL environment variables
set DB_HOST=
set DB_NAME=
set DB_USER=
set DB_PASSWORD=
set DB_PORT=

REM Run SQLite tests
pytest %PYTEST_ARGS% tests/unit/ tests/test_cors.py
if %ERRORLEVEL% equ 0 (
    echo ✅ SQLite tests passed!
    set SQLITE_PASSED=true
) else (
    echo ❌ SQLite tests failed!
    set SQLITE_PASSED=false
)
goto :eof

REM Function to run PostgreSQL tests
:run_postgres_tests
echo.
echo 🟢 Running PostgreSQL Integration Tests...

REM Check if PostgreSQL is running
echo Checking PostgreSQL connection...
psql -h localhost -p 5432 -U postgres -d test_db -c "SELECT 1;" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ PostgreSQL is not running or not accessible
    echo Please start PostgreSQL and ensure test_db database exists
    echo You can create the test database with: createdb -U postgres test_db
    set POSTGRES_PASSED=false
    goto :eof
)

REM Set PostgreSQL environment variables
set DB_HOST=localhost
set DB_PORT=5432
set DB_NAME=test_db
set DB_USER=postgres
set DB_PASSWORD=postgres
set ENVIRONMENT=test

REM Run PostgreSQL tests
pytest %PYTEST_ARGS% tests/integration/
if %ERRORLEVEL% equ 0 (
    echo ✅ PostgreSQL tests passed!
    set POSTGRES_PASSED=true
) else (
    echo ❌ PostgreSQL tests failed!
    set POSTGRES_PASSED=false
)
goto :eof

REM Main execution
set start_time=%TIME%
set SQLITE_PASSED=false
set POSTGRES_PASSED=false

if "%SQLITE_ONLY%"=="true" (
    call :run_sqlite_tests
) else if "%POSTGRES_ONLY%"=="true" (
    call :run_postgres_tests
) else if "%ALL_TESTS%"=="true" (
    echo Running both SQLite and PostgreSQL tests...
    call :run_sqlite_tests
    call :run_postgres_tests
)

REM Clean up environment variables
set DB_HOST=
set DB_NAME=
set DB_USER=
set DB_PASSWORD=
set DB_PORT=
set ENVIRONMENT=

REM Summary
echo.
echo 📊 Test Summary
echo ==============

if "%SQLITE_ONLY%"=="true" (
    if "%SQLITE_PASSED%"=="true" (
        echo ✅ All SQLite tests passed!
        exit /b 0
    ) else (
        echo ❌ SQLite tests failed!
        exit /b 1
    )
) else if "%POSTGRES_ONLY%"=="true" (
    if "%POSTGRES_PASSED%"=="true" (
        echo ✅ All PostgreSQL tests passed!
        exit /b 0
    ) else (
        echo ❌ PostgreSQL tests failed!
        exit /b 1
    )
) else (
    if "%SQLITE_PASSED%"=="true" if "%POSTGRES_PASSED%"=="true" (
        echo ✅ All tests passed!
        echo    - SQLite unit tests: ✅
        echo    - PostgreSQL integration tests: ✅
        exit /b 0
    ) else (
        echo ❌ Some tests failed!
        echo    - SQLite unit tests: %SQLITE_PASSED%
        echo    - PostgreSQL integration tests: %POSTGRES_PASSED%
        exit /b 1
    )
) 