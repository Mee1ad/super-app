#!/bin/bash

# PostgreSQL Test Database Setup Script for Linux/macOS
# Automates the creation of test database for hybrid testing

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Parse command line arguments
FORCE=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            FORCE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--force] [--verbose]"
            exit 1
            ;;
    esac
done

echo -e "${CYAN}🗄️ PostgreSQL Test Database Setup${NC}"
echo -e "${CYAN}=================================${NC}"

# Check if PostgreSQL is installed
echo -e "${YELLOW}Checking PostgreSQL installation...${NC}"

if command -v psql &> /dev/null; then
    PG_VERSION=$(psql --version)
    echo -e "${GREEN}✅ PostgreSQL found: $PG_VERSION${NC}"
else
    echo -e "${RED}❌ PostgreSQL not found${NC}"
    echo -e "${YELLOW}Please install PostgreSQL first:${NC}"
    echo -e "${GRAY}  Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib${NC}"
    echo -e "${GRAY}  macOS: brew install postgresql${NC}"
    echo -e "${GRAY}  CentOS/RHEL: sudo yum install postgresql postgresql-server${NC}"
    exit 1
fi

# Check if PostgreSQL service is running
echo -e "${YELLOW}Checking PostgreSQL service...${NC}"

# Detect OS and check service
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if brew services list | grep -q "postgresql.*started"; then
        echo -e "${GREEN}✅ PostgreSQL service is running${NC}"
    else
        echo -e "${YELLOW}⚠️ PostgreSQL service not running, attempting to start...${NC}"
        if brew services start postgresql; then
            echo -e "${GREEN}✅ PostgreSQL service started${NC}"
        else
            echo -e "${RED}❌ Failed to start PostgreSQL service${NC}"
            echo -e "${YELLOW}Please start PostgreSQL manually: brew services start postgresql${NC}"
            exit 1
        fi
    fi
else
    # Linux
    if systemctl is-active --quiet postgresql; then
        echo -e "${GREEN}✅ PostgreSQL service is running${NC}"
    else
        echo -e "${YELLOW}⚠️ PostgreSQL service not running, attempting to start...${NC}"
        if sudo systemctl start postgresql; then
            echo -e "${GREEN}✅ PostgreSQL service started${NC}"
        else
            echo -e "${RED}❌ Failed to start PostgreSQL service${NC}"
            echo -e "${YELLOW}Please start PostgreSQL manually: sudo systemctl start postgresql${NC}"
            exit 1
        fi
    fi
fi

# Test connection to PostgreSQL
echo -e "${YELLOW}Testing PostgreSQL connection...${NC}"

if pg_isready -h localhost -p 5432 -U postgres >/dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL connection successful${NC}"
    if [[ "$VERBOSE" == true ]]; then
        VERSION=$(psql -h localhost -p 5432 -U postgres -c "SELECT version();" -t 2>/dev/null | head -1)
        echo -e "${GRAY}Server version: $VERSION${NC}"
    fi
else
    echo -e "${RED}❌ PostgreSQL connection failed${NC}"
    echo -e "${YELLOW}Please check your PostgreSQL configuration${NC}"
    exit 1
fi

# Check if test database exists
echo -e "${YELLOW}Checking if test database exists...${NC}"

if psql -h localhost -p 5432 -U postgres -d test_db -c "SELECT 1;" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Test database 'test_db' already exists${NC}"
    if [[ "$FORCE" == false ]]; then
        echo -e "${YELLOW}Use --force to recreate the database${NC}"
        exit 0
    else
        echo -e "${YELLOW}Recreating test database...${NC}"
    fi
else
    echo -e "${YELLOW}Test database 'test_db' does not exist${NC}"
fi

# Create test database
echo -e "${YELLOW}Creating test database...${NC}"

if [[ "$FORCE" == true ]]; then
    # Drop existing database if force flag is used
    echo -e "${YELLOW}Dropping existing test database...${NC}"
    dropdb -h localhost -p 5432 -U postgres test_db 2>/dev/null || true
fi

# Create new database
if createdb -h localhost -p 5432 -U postgres test_db 2>/dev/null; then
    echo -e "${GREEN}✅ Test database 'test_db' created successfully${NC}"
else
    echo -e "${RED}❌ Failed to create test database${NC}"
    echo -e "${YELLOW}Please check your PostgreSQL permissions${NC}"
    exit 1
fi

# Test the new database
echo -e "${YELLOW}Testing new database...${NC}"

if psql -h localhost -p 5432 -U postgres -d test_db -c "SELECT 'Test database is ready!' as status;" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Test database is ready!${NC}"
else
    echo -e "${RED}❌ Test database verification failed${NC}"
    exit 1
fi

# Set up environment variables for testing
echo -e "${YELLOW}Setting up environment variables...${NC}"

export DB_HOST="localhost"
export DB_PORT="5432"
export DB_NAME="test_db"
export DB_USER="postgres"
export DB_PASSWORD="postgres"
export ENVIRONMENT="test"

echo -e "\n${GREEN}🎉 PostgreSQL Test Database Setup Complete!${NC}"
echo -e "${GREEN}=============================================${NC}"
echo -e "${GRAY}Database: test_db${NC}"
echo -e "${GRAY}Host: localhost${NC}"
echo -e "${GRAY}Port: 5432${NC}"
echo -e "${GRAY}User: postgres${NC}"

echo -e "\n${CYAN}📝 Next Steps:${NC}"
echo -e "${GRAY}1. Run SQLite tests: ./scripts/run-tests.sh --sqlite-only${NC}"
echo -e "${GRAY}2. Run PostgreSQL tests: ./scripts/run-tests.sh --postgres-only${NC}"
echo -e "${GRAY}3. Run all tests: ./scripts/run-tests.sh${NC}"

echo -e "\n${YELLOW}💡 Note: Environment variables are set for this session only.${NC}"
echo -e "${YELLOW}   For persistent setup, add them to your environment or .env file.${NC}"

# Create a .env.test file for easy setup
cat > .env.test << EOF
# PostgreSQL Test Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=test_db
DB_USER=postgres
DB_PASSWORD=postgres
ENVIRONMENT=test
EOF

echo -e "\n${CYAN}📄 Created .env.test file for easy environment setup${NC}"
echo -e "${GRAY}   You can source it with: source .env.test${NC}" 