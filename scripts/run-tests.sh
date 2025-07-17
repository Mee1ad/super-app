#!/bin/bash

# Hybrid Testing Script for Linux/macOS
# Runs both SQLite unit tests and PostgreSQL integration tests

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Parse command line arguments
SQLITE_ONLY=false
POSTGRES_ONLY=false
ALL_TESTS=false
COVERAGE=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --sqlite-only)
            SQLITE_ONLY=true
            shift
            ;;
        --postgres-only)
            POSTGRES_ONLY=true
            shift
            ;;
        --all-tests)
            ALL_TESTS=true
            shift
            ;;
        --coverage)
            COVERAGE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--sqlite-only] [--postgres-only] [--all-tests] [--coverage] [--verbose]"
            exit 1
            ;;
    esac
done

# Default to all tests if no specific option is provided
if [[ "$SQLITE_ONLY" == false && "$POSTGRES_ONLY" == false && "$ALL_TESTS" == false ]]; then
    ALL_TESTS=true
fi

echo -e "${CYAN}🧪 Hybrid Testing Strategy${NC}"
echo -e "${CYAN}=========================${NC}"

# Build pytest arguments
PYTEST_ARGS=()
if [[ "$VERBOSE" == true ]]; then
    PYTEST_ARGS+=("-v" "-s")
else
    PYTEST_ARGS+=("-v")
fi

if [[ "$COVERAGE" == true ]]; then
    PYTEST_ARGS+=("--cov=apps" "--cov=db" "--cov=core" "--cov-report=term-missing")
fi

# Function to run SQLite tests
run_sqlite_tests() {
    echo -e "\n${BLUE}🔵 Running SQLite Unit Tests...${NC}"
    
    # Clear any PostgreSQL environment variables
    unset DB_HOST DB_NAME DB_USER DB_PASSWORD DB_PORT
    
    # Run SQLite tests
    if pytest "${PYTEST_ARGS[@]}" tests/unit/ tests/test_cors.py; then
        echo -e "${GREEN}✅ SQLite tests passed!${NC}"
        return 0
    else
        echo -e "${RED}❌ SQLite tests failed!${NC}"
        return 1
    fi
}

# Function to run PostgreSQL tests
run_postgres_tests() {
    echo -e "\n${GREEN}🟢 Running PostgreSQL Integration Tests...${NC}"
    
    # Check if PostgreSQL is running
    echo -e "${YELLOW}Checking PostgreSQL connection...${NC}"
    if ! pg_isready -h localhost -p 5432 -U postgres >/dev/null 2>&1; then
        echo -e "${RED}❌ PostgreSQL is not running or not accessible${NC}"
        echo -e "${YELLOW}Please start PostgreSQL and ensure test_db database exists${NC}"
        echo -e "${YELLOW}You can create the test database with: createdb -U postgres test_db${NC}"
        return 1
    fi
    
    # Test database connection
    if ! psql -h localhost -p 5432 -U postgres -d test_db -c "SELECT 1;" >/dev/null 2>&1; then
        echo -e "${RED}❌ Cannot connect to test_db database${NC}"
        echo -e "${YELLOW}Please create the test database: createdb -U postgres test_db${NC}"
        return 1
    fi
    
    # Set PostgreSQL environment variables
    export DB_HOST="localhost"
    export DB_PORT="5432"
    export DB_NAME="test_db"
    export DB_USER="postgres"
    export DB_PASSWORD="postgres"
    export ENVIRONMENT="test"
    
    # Run PostgreSQL tests
    if pytest "${PYTEST_ARGS[@]}" tests/integration/; then
        echo -e "${GREEN}✅ PostgreSQL tests passed!${NC}"
        return 0
    else
        echo -e "${RED}❌ PostgreSQL tests failed!${NC}"
        return 1
    fi
}

# Main execution
start_time=$(date +%s)
sqlite_passed=false
postgres_passed=false

# Cleanup function
cleanup() {
    # Clean up environment variables
    unset DB_HOST DB_NAME DB_USER DB_PASSWORD DB_PORT ENVIRONMENT
}

# Set trap to ensure cleanup runs
trap cleanup EXIT

if [[ "$SQLITE_ONLY" == true ]]; then
    if run_sqlite_tests; then
        sqlite_passed=true
    fi
elif [[ "$POSTGRES_ONLY" == true ]]; then
    if run_postgres_tests; then
        postgres_passed=true
    fi
elif [[ "$ALL_TESTS" == true ]]; then
    echo -e "${CYAN}Running both SQLite and PostgreSQL tests...${NC}"
    if run_sqlite_tests; then
        sqlite_passed=true
    fi
    if run_postgres_tests; then
        postgres_passed=true
    fi
fi

# Summary
end_time=$(date +%s)
duration=$((end_time - start_time))

echo -e "\n${CYAN}📊 Test Summary${NC}"
echo -e "${CYAN}==============${NC}"
echo -e "${GRAY}Duration: ${duration} seconds${NC}"

if [[ "$SQLITE_ONLY" == true ]]; then
    if [[ "$sqlite_passed" == true ]]; then
        echo -e "${GREEN}✅ All SQLite tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}❌ SQLite tests failed!${NC}"
        exit 1
    fi
elif [[ "$POSTGRES_ONLY" == true ]]; then
    if [[ "$postgres_passed" == true ]]; then
        echo -e "${GREEN}✅ All PostgreSQL tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}❌ PostgreSQL tests failed!${NC}"
        exit 1
    fi
else
    if [[ "$sqlite_passed" == true && "$postgres_passed" == true ]]; then
        echo -e "${GREEN}✅ All tests passed!${NC}"
        echo -e "   - SQLite unit tests: ${GREEN}✅${NC}"
        echo -e "   - PostgreSQL integration tests: ${GREEN}✅${NC}"
        exit 0
    else
        echo -e "${RED}❌ Some tests failed!${NC}"
        echo -e "   - SQLite unit tests: $(if [[ "$sqlite_passed" == true ]]; then echo -e "${GREEN}✅${NC}"; else echo -e "${RED}❌${NC}"; fi)"
        echo -e "   - PostgreSQL integration tests: $(if [[ "$postgres_passed" == true ]]; then echo -e "${GREEN}✅${NC}"; else echo -e "${RED}❌${NC}"; fi)"
        exit 1
    fi
fi 