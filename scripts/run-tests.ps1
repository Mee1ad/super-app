# Hybrid Testing Script for Windows
# Runs both SQLite unit tests and PostgreSQL integration tests

param(
    [switch]$SqliteOnly,
    [switch]$PostgresOnly,
    [switch]$AllTests,
    [switch]$Coverage,
    [switch]$Verbose
)

Write-Host "🧪 Hybrid Testing Strategy" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

# Default to all tests if no specific option is provided
if (-not $SqliteOnly -and -not $PostgresOnly -and -not $AllTests) {
    $AllTests = $true
}

# Build pytest arguments
$pytestArgs = @()
if ($Verbose) {
    $pytestArgs += "-v", "-s"
} else {
    $pytestArgs += "-v"
}

if ($Coverage) {
    $pytestArgs += "--cov=apps", "--cov=db", "--cov=core", "--cov-report=term-missing"
}

# Function to run SQLite tests
function Run-SqliteTests {
    Write-Host "`n🔵 Running SQLite Unit Tests..." -ForegroundColor Blue
    
    # Clear any PostgreSQL environment variables
    $env:DB_HOST = $null
    $env:DB_NAME = $null
    $env:DB_USER = $null
    $env:DB_PASSWORD = $null
    $env:DB_PORT = $null
    
    # Run SQLite tests
    $sqliteArgs = $pytestArgs + @("tests/unit/", "tests/test_cors.py")
    $result = pytest @sqliteArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ SQLite tests passed!" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ SQLite tests failed!" -ForegroundColor Red
        return $false
    }
}

# Function to run PostgreSQL tests
function Run-PostgresTests {
    Write-Host "`n🟢 Running PostgreSQL Integration Tests..." -ForegroundColor Green
    
    # Check if PostgreSQL is running
    Write-Host "Checking PostgreSQL connection..." -ForegroundColor Yellow
    try {
        $pgTest = psql -h localhost -p 5432 -U postgres -d test_db -c "SELECT 1;" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ PostgreSQL is not running or not accessible" -ForegroundColor Red
            Write-Host "Please start PostgreSQL and ensure test_db database exists" -ForegroundColor Yellow
            Write-Host "You can create the test database with: createdb -U postgres test_db" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "❌ PostgreSQL connection failed" -ForegroundColor Red
        return $false
    }
    
    # Set PostgreSQL environment variables
    $env:DB_HOST = "localhost"
    $env:DB_PORT = "5432"
    $env:DB_NAME = "test_db"
    $env:DB_USER = "postgres"
    $env:DB_PASSWORD = "postgres"
    $env:ENVIRONMENT = "test"
    
    # Run PostgreSQL tests
    $postgresArgs = $pytestArgs + @("tests/integration/")
    $result = pytest @postgresArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ PostgreSQL tests passed!" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ PostgreSQL tests failed!" -ForegroundColor Red
        return $false
    }
}

# Main execution
$startTime = Get-Date
$sqlitePassed = $false
$postgresPassed = $false

try {
    if ($SqliteOnly) {
        $sqlitePassed = Run-SqliteTests
    } elseif ($PostgresOnly) {
        $postgresPassed = Run-PostgresTests
    } elseif ($AllTests) {
        Write-Host "Running both SQLite and PostgreSQL tests..." -ForegroundColor Cyan
        $sqlitePassed = Run-SqliteTests
        $postgresPassed = Run-PostgresTests
    }
} finally {
    # Clean up environment variables
    $env:DB_HOST = $null
    $env:DB_NAME = $null
    $env:DB_USER = $null
    $env:DB_PASSWORD = $null
    $env:DB_PORT = $null
    $env:ENVIRONMENT = $null
}

# Summary
$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host "`n📊 Test Summary" -ForegroundColor Cyan
Write-Host "==============" -ForegroundColor Cyan
Write-Host "Duration: $($duration.TotalSeconds.ToString('F2')) seconds" -ForegroundColor Gray

if ($SqliteOnly) {
    if ($sqlitePassed) {
        Write-Host "✅ All SQLite tests passed!" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "❌ SQLite tests failed!" -ForegroundColor Red
        exit 1
    }
} elseif ($PostgresOnly) {
    if ($postgresPassed) {
        Write-Host "✅ All PostgreSQL tests passed!" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "❌ PostgreSQL tests failed!" -ForegroundColor Red
        exit 1
    }
} else {
    if ($sqlitePassed -and $postgresPassed) {
        Write-Host "✅ All tests passed!" -ForegroundColor Green
        Write-Host "   - SQLite unit tests: ✅" -ForegroundColor Green
        Write-Host "   - PostgreSQL integration tests: ✅" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "❌ Some tests failed!" -ForegroundColor Red
        Write-Host "   - SQLite unit tests: $(if ($sqlitePassed) { '✅' } else { '❌' })" -ForegroundColor $(if ($sqlitePassed) { 'Green' } else { 'Red' })
        Write-Host "   - PostgreSQL integration tests: $(if ($postgresPassed) { '✅' } else { '❌' })" -ForegroundColor $(if ($postgresPassed) { 'Green' } else { 'Red' })
        exit 1
    }
} 