#!/bin/bash

# Environment Setup Script
# This script helps set up different environments for the super-app-backend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [environment]"
    echo ""
    echo "Environments:"
    echo "  dev|development  - Set up development environment (default)"
    echo "  prod|production  - Set up production environment"
    echo "  test             - Set up test environment"
    echo ""
    echo "Examples:"
    echo "  $0 dev           # Set up development environment"
    echo "  $0 production    # Set up production environment"
    echo "  $0               # Set up development environment (default)"
}

# Function to setup development environment
setup_development() {
    print_status "Setting up development environment..."
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        print_status "Creating .env file with development settings..."
        
        # Create .env with actual development values
        cat > .env << 'EOF'
# Development Environment Configuration
# This file contains actual development settings
# DO NOT commit this file to version control

# Environment
ENVIRONMENT=development

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=superapp
DB_USER=postgres
DB_PASSWORD=admin

# Security
SECRET_KEY=your-secret-key-here

# Debug mode
DEBUG=true
EOF
        
        print_success "Created .env file with development settings"
        print_warning "Please update SECRET_KEY and API_KEY with your actual values"
    else
        print_warning ".env file already exists, skipping creation"
    fi
    
    # Set environment variables
    export ENVIRONMENT="development"
    export DB_HOST="localhost"
    export DB_PORT="5432"
    export DB_NAME="superapp"
    export DB_USER="postgres"
    export DB_PASSWORD="admin"
    export DEBUG="true"
    
    print_success "Development environment configured"
    print_status "Database: $DB_HOST:$DB_PORT/$DB_NAME"
    print_status "Environment: $ENVIRONMENT"
    print_status "Debug: $DEBUG"
}

# Function to setup production environment
setup_production() {
    print_status "Setting up production environment..."
    
    # Check if production env file exists
    if [ ! -f env.production ]; then
        print_error "env.production file not found!"
        print_status "Please create env.production file with production settings"
        exit 1
    fi
    
    # Load production environment
    export $(cat env.production | grep -v '^#' | xargs)
    
    print_success "Production environment configured"
    print_status "Database URL: $DATABASE_URL"
    print_status "Environment: $ENVIRONMENT"
    print_status "Debug: $DEBUG"
    
    # Security warning
    print_warning "Make sure env.production is in .gitignore"
    print_warning "Never commit production credentials to version control"
}

# Function to setup test environment
setup_test() {
    print_status "Setting up test environment..."
    
    # Set test environment variables
    export ENVIRONMENT="test"
    export DB_HOST="localhost"
    export DB_PORT="5432"
    export DB_NAME="lifehub_test"
    export DB_USER="postgres"
    export DB_PASSWORD="admin"
    export DEBUG="true"
    
    print_success "Test environment configured"
    print_status "Database: $DB_HOST:$DB_PORT/$DB_NAME"
    print_status "Environment: $ENVIRONMENT"
    print_status "Debug: $DEBUG"
}

# Function to validate environment
validate_environment() {
    print_status "Validating environment configuration..."
    
    # Check if required files exist
    if [ ! -f core/config.py ]; then
        print_error "core/config.py not found!"
        exit 1
    fi
    
    if [ ! -f db/session.py ]; then
        print_error "db/session.py not found!"
        exit 1
    fi
    
    # Test database connection (if possible)
    if command -v psql &> /dev/null; then
        print_status "Testing database connection..."
        # Build database URL from components
        DB_URL="postgresql://${DB_USER:-postgres}:${DB_PASSWORD:-admin}@${DB_HOST:-localhost}:${DB_PORT:-5432}/${DB_NAME:-superapp}"
        
        # Simple connection test (this is a basic test)
        if echo "SELECT 1;" | psql "$DB_URL" > /dev/null 2>&1; then
            print_success "Database connection successful"
        else
            print_warning "Database connection failed - make sure PostgreSQL is running"
        fi
    else
        print_warning "psql not found - skipping database connection test"
    fi
    
    print_success "Environment validation completed"
}

# Main script logic
main() {
    local env=${1:-"dev"}
    
    print_status "Super App Backend - Environment Setup"
    print_status "Setting up environment: $env"
    
    case $env in
        "dev"|"development")
            setup_development
            ;;
        "prod"|"production")
            setup_production
            ;;
        "test")
            setup_test
            ;;
        "help"|"-h"|"--help")
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown environment: $env"
            show_usage
            exit 1
            ;;
    esac
    
    validate_environment
    
    print_success "Environment setup completed successfully!"
    print_status "You can now run your application with the configured environment"
}

# Run main function with all arguments
main "$@" 