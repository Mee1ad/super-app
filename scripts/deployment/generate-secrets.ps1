# Generate Secure Secrets Script
# This script generates cryptographically secure secret keys

param(
    [string]$Type = "all"
)

# Function to show usage
function Show-Usage {
    Write-Host "Usage: .\scripts\generate-secrets.ps1 [type]" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Types:" -ForegroundColor White
    Write-Host "  all        - Generate both SECRET_KEY and API_KEY (default)" -ForegroundColor Yellow
    Write-Host "  secret     - Generate SECRET_KEY only" -ForegroundColor Yellow
    Write-Host "  api        - Generate API_KEY only" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor White
    Write-Host "  .\scripts\generate-secrets.ps1 all        # Generate both keys" -ForegroundColor Gray
    Write-Host "  .\scripts\generate-secrets.ps1 secret     # Generate SECRET_KEY only" -ForegroundColor Gray
    Write-Host "  .\scripts\generate-secrets.ps1 api        # Generate API_KEY only" -ForegroundColor Gray
}

# Function to generate SECRET_KEY
function Generate-SecretKey {
    Write-Host "Generating SECRET_KEY..." -ForegroundColor Blue
    $secretKey = python -c "import secrets; print(secrets.token_urlsafe(32))"
    Write-Host "SECRET_KEY=$secretKey" -ForegroundColor Green
    return $secretKey
}

# Function to update .env file
function Update-EnvFile {
    param(
        [string]$SecretKey
    )
    
    if (Test-Path ".env") {
        Write-Host "Updating .env file..." -ForegroundColor Blue
        
        $content = Get-Content .env
        
        if ($SecretKey) {
            $content = $content -replace 'SECRET_KEY=.*', "SECRET_KEY=$SecretKey"
        }
        
        $content | Set-Content .env
        Write-Host "✅ .env file updated successfully" -ForegroundColor Green
    } else {
        Write-Host "⚠️  .env file not found. Key generated but not saved." -ForegroundColor Yellow
    }
}

# Main script logic
Write-Host "🔐 Secure Key Generator" -ForegroundColor Cyan
Write-Host "Generating key for type: $Type" -ForegroundColor Blue

$secretKey = $null

switch ($Type.ToLower()) {
    "all" {
        $secretKey = Generate-SecretKey
    }
    "secret" {
        $secretKey = Generate-SecretKey
    }
    { $_ -in @("help", "-h", "--help") } {
        Show-Usage
        exit 0
    }
    default {
        Write-Host "[ERROR] Unknown type: $Type" -ForegroundColor Red
        Show-Usage
        exit 1
    }
}

# Update .env file if key was generated
if ($secretKey) {
    Update-EnvFile -SecretKey $secretKey
}

Write-Host ""
Write-Host "🔑 Generated Key:" -ForegroundColor Cyan
if ($secretKey) {
    Write-Host "SECRET_KEY=$secretKey" -ForegroundColor White
}

Write-Host ""
Write-Host "✅ Key generation completed successfully!" -ForegroundColor Green
Write-Host "💡 Remember to keep this key secure and never commit it to version control." -ForegroundColor Yellow 