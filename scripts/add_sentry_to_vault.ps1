#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Add Sentry DSN to Ansible vault for production deployment

.DESCRIPTION
    This script helps you add the Sentry DSN to the Ansible vault file
    so that it can be used in production deployment.

.PARAMETER SentryDsn
    Your Sentry DSN (e.g., https://your-key@sentry.io/project-id)

.EXAMPLE
    .\add_sentry_to_vault.ps1 -SentryDsn "https://your-key@sentry.io/project-id"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$SentryDsn
)

# Check if ansible-vault is available
try {
    $ansibleVaultVersion = ansible-vault --version
    Write-Host "✅ Ansible vault found: $ansibleVaultVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Ansible vault not found. Please install Ansible first." -ForegroundColor Red
    Write-Host "Install with: pip install ansible" -ForegroundColor Yellow
    exit 1
}

# Create a temporary file with the new variable
$tempFile = "temp_vault_vars.yml"
@"
vault_sentry_dsn: "$SentryDsn"
"@ | Out-File -FilePath $tempFile -Encoding UTF8

Write-Host "🔐 Adding Sentry DSN to Ansible vault..." -ForegroundColor Yellow

# Add the variable to the vault
try {
    ansible-vault encrypt_string --vault-id vault.yml "$SentryDsn" --name vault_sentry_dsn
    Write-Host "✅ Sentry DSN added to vault successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 Next steps:" -ForegroundColor Cyan
    Write-Host "1. Copy the encrypted output above" -ForegroundColor White
    Write-Host "2. Add it to ansible/group_vars/vault.yml" -ForegroundColor White
    Write-Host "3. Deploy to production with: .\scripts\ansible\run-ansible-deploy.ps1" -ForegroundColor White
} catch {
    Write-Host "❌ Failed to add to vault: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    # Clean up
    if (Test-Path $tempFile) {
        Remove-Item $tempFile
    }
} 