# Environment Setup Script for Windows
# This script helps set up different environments for the super-app-backend

param(
    [string]$Environment = "dev"
)

# Function to show usage
function Show-Usage {
    Write-Host "Usage: .\scripts\setup-env.ps1 [environment]" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Environments:" -ForegroundColor White
    Write-Host "  dev|development  - Set up development environment (default)" -ForegroundColor Yellow
    Write-Host "  prod|production  - Set up production environment" -ForegroundColor Yellow
    Write-Host "  test             - Set up test environment" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor White
    Write-Host "  .\scripts\setup-env.ps1 dev           # Set up development environment" -ForegroundColor Gray
    Write-Host "  .\scripts\setup-env.ps1 production    # Set up production environment" -ForegroundColor Gray
    Write-Host "  .\scripts\setup-env.ps1               # Set up development environment (default)" -ForegroundColor Gray
}

# Function to setup development environment
function Setup-Development {
    Write-Host "[INFO] Setting up development environment..." -ForegroundColor Blue
    
    # Create .env file if it doesn't exist
    if (-not (Test-Path ".env")) {
        Write-Host "[INFO] Creating .env file with development settings..." -ForegroundColor Blue
        
        # Create .env with actual development values
        @"
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
"@ | Out-File -FilePath ".env" -Encoding UTF8
        
        Write-Host "[SUCCESS] Created .env file with development settings" -ForegroundColor Green
        Write-Host "[INFO] Please update SECRET_KEY and API_KEY with your actual values" -ForegroundColor Yellow
    } else {
        Write-Host "[WARNING] .env file already exists, skipping creation" -ForegroundColor Yellow
    }
    
    # Set environment variables
    $env:ENVIRONMENT = "development"
    $env:DB_HOST = "localhost"
    $env:DB_PORT = "5432"
    $env:DB_NAME = "superapp"
    $env:DB_USER = "postgres"
    $env:DB_PASSWORD = "admin"
    $env:DEBUG = "true"
    
    Write-Host "[SUCCESS] Development environment configured" -ForegroundColor Green
    Write-Host "[INFO] Database: $env:DB_HOST:$env:DB_PORT/$env:DB_NAME" -ForegroundColor Blue
    Write-Host "[INFO] Environment: $env:ENVIRONMENT" -ForegroundColor Blue
    Write-Host "[INFO] Debug: $env:DEBUG" -ForegroundColor Blue
}

# Function to setup production environment
function Setup-Production {
    Write-Host "[INFO] Setting up production environment..." -ForegroundColor Blue
    
    # Check if production env file exists
    if (-not (Test-Path "env.production")) {
        Write-Host "[ERROR] env.production file not found!" -ForegroundColor Red
        Write-Host "[INFO] Please create env.production file with production settings" -ForegroundColor Blue
        exit 1
    }
    
    # Load production environment
    Get-Content "env.production" | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            $name = $matches[1]
            $value = $matches[2]
            Set-Item -Path "env:$name" -Value $value
        }
    }
    
    Write-Host "[SUCCESS] Production environment configured" -ForegroundColor Green
    Write-Host "[INFO] Database URL: $env:DATABASE_URL" -ForegroundColor Blue
    Write-Host "[INFO] Environment: $env:ENVIRONMENT" -ForegroundColor Blue
    Write-Host "[INFO] Debug: $env:DEBUG" -ForegroundColor Blue
    
    # Security warning
    Write-Host "[WARNING] Make sure env.production is in .gitignore" -ForegroundColor Yellow
    Write-Host "[WARNING] Never commit production credentials to version control" -ForegroundColor Yellow
}

# Function to setup test environment
function Setup-Test {
    Write-Host "[INFO] Setting up test environment..." -ForegroundColor Blue
    
    # Set test environment variables
    $env:ENVIRONMENT = "test"
    $env:DATABASE_URL = "postgresql://postgres:admin@localhost:5432/lifehub_test"
    $env:DEBUG = "true"
    
    Write-Host "[SUCCESS] Test environment configured" -ForegroundColor Green
    Write-Host "[INFO] Database URL: $env:DATABASE_URL" -ForegroundColor Blue
    Write-Host "[INFO] Environment: $env:ENVIRONMENT" -ForegroundColor Blue
    Write-Host "[INFO] Debug: $env:DEBUG" -ForegroundColor Blue
}

# Function to validate environment
function Test-Environment {
    Write-Host "[INFO] Validating environment configuration..." -ForegroundColor Blue
    
    # Check if required files exist
    if (-not (Test-Path "core/config.py")) {
        Write-Host "[ERROR] core/config.py not found!" -ForegroundColor Red
        exit 1
    }
    
    if (-not (Test-Path "db/session.py")) {
        Write-Host "[ERROR] db/session.py not found!" -ForegroundColor Red
        exit 1
    }
    
    # Test database connection (if possible)
    try {
        $psqlPath = Get-Command psql -ErrorAction SilentlyContinue
        if ($psqlPath) {
            Write-Host "[INFO] Testing database connection..." -ForegroundColor Blue
            $DB_URL = "postgresql://$($env:DB_USER):$($env:DB_PASSWORD)@$($env:DB_HOST):$($env:DB_PORT)/$($env:DB_NAME)"
            
            # Simple connection test
            $result = & psql $DB_URL -c "SELECT 1;" 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "[SUCCESS] Database connection successful" -ForegroundColor Green
            } else {
                Write-Host "[WARNING] Database connection failed - make sure PostgreSQL is running" -ForegroundColor Yellow
            }
        } else {
            Write-Host "[WARNING] psql not found - skipping database connection test" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "[WARNING] Could not test database connection: $($_.Exception.Message)" -ForegroundColor Yellow
    }
    
    Write-Host "[SUCCESS] Environment validation completed" -ForegroundColor Green
}

# Main script logic
Write-Host "Super App Backend - Environment Setup" -ForegroundColor Cyan
Write-Host "Setting up environment: $Environment" -ForegroundColor Blue

switch ($Environment.ToLower()) {
    { $_ -in @("dev", "development") } {
        Setup-Development
    }
    { $_ -in @("prod", "production") } {
        Setup-Production
    }
    "test" {
        Setup-Test
    }
    { $_ -in @("help", "-h", "--help") } {
        Show-Usage
        exit 0
    }
    default {
        Write-Host "[ERROR] Unknown environment: $Environment" -ForegroundColor Red
        Show-Usage
        exit 1
    }
}

Test-Environment

Write-Host "[SUCCESS] Environment setup completed successfully!" -ForegroundColor Green
Write-Host "[INFO] You can now run your application with the configured environment" -ForegroundColor Blue 