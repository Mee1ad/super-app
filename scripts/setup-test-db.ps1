# PostgreSQL Test Database Setup Script for Windows
# Automates the creation of test database for hybrid testing

param(
    [switch]$Force,
    [switch]$Verbose
)

Write-Host "🗄️ PostgreSQL Test Database Setup" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Check if PostgreSQL is installed
Write-Host "Checking PostgreSQL installation..." -ForegroundColor Yellow

try {
    $pgVersion = psql --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ PostgreSQL found: $pgVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ PostgreSQL not found in PATH" -ForegroundColor Red
        Write-Host "Please install PostgreSQL and add it to your PATH" -ForegroundColor Yellow
        Write-Host "You can install it with: choco install postgresql" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ PostgreSQL not found" -ForegroundColor Red
    Write-Host "Please install PostgreSQL first" -ForegroundColor Yellow
    exit 1
}

# Check if PostgreSQL service is running
Write-Host "Checking PostgreSQL service..." -ForegroundColor Yellow
try {
    $service = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
    if ($service -and $service.Status -eq "Running") {
        Write-Host "✅ PostgreSQL service is running" -ForegroundColor Green
    } else {
        Write-Host "⚠️ PostgreSQL service not running, attempting to start..." -ForegroundColor Yellow
        try {
            Start-Service -Name "postgresql*" -ErrorAction Stop
            Write-Host "✅ PostgreSQL service started" -ForegroundColor Green
        } catch {
            Write-Host "❌ Failed to start PostgreSQL service" -ForegroundColor Red
            Write-Host "Please start PostgreSQL manually" -ForegroundColor Yellow
            exit 1
        }
    }
} catch {
    Write-Host "⚠️ Could not check PostgreSQL service status" -ForegroundColor Yellow
    Write-Host "Continuing with connection test..." -ForegroundColor Yellow
}

# Test connection to PostgreSQL
Write-Host "Testing PostgreSQL connection..." -ForegroundColor Yellow
try {
    $testResult = psql -h localhost -p 5432 -U postgres -c "SELECT version();" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ PostgreSQL connection successful" -ForegroundColor Green
        if ($Verbose) {
            Write-Host "Server version: $testResult" -ForegroundColor Gray
        }
    } else {
        Write-Host "❌ PostgreSQL connection failed" -ForegroundColor Red
        Write-Host "Please check your PostgreSQL configuration" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ PostgreSQL connection failed" -ForegroundColor Red
    Write-Host "Please ensure PostgreSQL is running and accessible" -ForegroundColor Yellow
    exit 1
}

# Check if test database exists
Write-Host "Checking if test database exists..." -ForegroundColor Yellow
try {
    $dbExists = psql -h localhost -p 5432 -U postgres -d test_db -c "SELECT 1;" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Test database 'test_db' already exists" -ForegroundColor Green
        if (-not $Force) {
            Write-Host "Use -Force to recreate the database" -ForegroundColor Yellow
            exit 0
        } else {
            Write-Host "Recreating test database..." -ForegroundColor Yellow
        }
    } else {
        Write-Host "Test database 'test_db' does not exist" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Test database 'test_db' does not exist" -ForegroundColor Yellow
}

# Create test database
Write-Host "Creating test database..." -ForegroundColor Yellow
try {
    if ($Force) {
        # Drop existing database if force flag is used
        Write-Host "Dropping existing test database..." -ForegroundColor Yellow
        dropdb -h localhost -p 5432 -U postgres test_db 2>$null
    }
    
    # Create new database
    $createResult = createdb -h localhost -p 5432 -U postgres test_db 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Test database 'test_db' created successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to create test database" -ForegroundColor Red
        Write-Host "Error: $createResult" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Failed to create test database" -ForegroundColor Red
    Write-Host "Please check your PostgreSQL permissions" -ForegroundColor Yellow
    exit 1
}

# Test the new database
Write-Host "Testing new database..." -ForegroundColor Yellow
try {
    $testResult = psql -h localhost -p 5432 -U postgres -d test_db -c "SELECT 'Test database is ready!' as status;" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Test database is ready!" -ForegroundColor Green
        if ($Verbose) {
            Write-Host "Test result: $testResult" -ForegroundColor Gray
        }
    } else {
        Write-Host "❌ Test database verification failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Test database verification failed" -ForegroundColor Red
    exit 1
}

# Set up environment variables for testing
Write-Host "Setting up environment variables..." -ForegroundColor Yellow
$env:DB_HOST = "localhost"
$env:DB_PORT = "5432"
$env:DB_NAME = "test_db"
$env:DB_USER = "postgres"
$env:DB_PASSWORD = "postgres"
$env:ENVIRONMENT = "test"

Write-Host "`n🎉 PostgreSQL Test Database Setup Complete!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host "Database: test_db" -ForegroundColor Gray
Write-Host "Host: localhost" -ForegroundColor Gray
Write-Host "Port: 5432" -ForegroundColor Gray
Write-Host "User: postgres" -ForegroundColor Gray

Write-Host "`n📝 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Run SQLite tests: .\scripts\run-tests.ps1 -SqliteOnly" -ForegroundColor Gray
Write-Host "2. Run PostgreSQL tests: .\scripts\run-tests.ps1 -PostgresOnly" -ForegroundColor Gray
Write-Host "3. Run all tests: .\scripts\run-tests.ps1" -ForegroundColor Gray

Write-Host "`n💡 Note: Environment variables are set for this session only." -ForegroundColor Yellow
Write-Host "   For persistent setup, add them to your environment or .env file." -ForegroundColor Yellow 