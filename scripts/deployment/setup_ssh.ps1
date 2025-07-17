# SSH Key Setup Script for Ansible Deployment
# This script helps manage SSH keys for Windows environment

param(
    [string]$KeyType = "ed25519",
    [string]$KeyPath = "~/.ssh/super-app-backend",
    [string]$Force = $false
)

Write-Host "SSH Key Setup for Ansible Deployment" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Expand the tilde to user's home directory
$KeyPath = $KeyPath -replace "~", $env:USERPROFILE

# Check if SSH directory exists
$sshDir = Split-Path $KeyPath -Parent
if (-not (Test-Path $sshDir)) {
    Write-Host "Creating SSH directory: $sshDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $sshDir -Force
}

# Check if SSH key already exists
if ((Test-Path $KeyPath) -and ($Force -eq $false)) {
    Write-Host "SSH key already exists at: $KeyPath" -ForegroundColor Yellow
    Write-Host "Use -Force parameter to overwrite existing key" -ForegroundColor Yellow
    exit 0
}

# Generate SSH key
Write-Host "Generating $KeyType SSH key..." -ForegroundColor Yellow
$sshKeygenArgs = @(
    "-t", $KeyType,
    "-f", $KeyPath,
    "-N", '""'
)

try {
    & ssh-keygen @sshKeygenArgs
    if ($LASTEXITCODE -eq 0) {
        Write-Host "SSH key generated successfully!" -ForegroundColor Green
        Write-Host "Private key: $KeyPath" -ForegroundColor Cyan
        Write-Host "Public key: $KeyPath.pub" -ForegroundColor Cyan
        
        # Display public key for easy copying
        Write-Host "`nPublic key content:" -ForegroundColor Yellow
        Get-Content "$KeyPath.pub" | Write-Host -ForegroundColor White
        
        Write-Host "`nNext steps:" -ForegroundColor Green
        Write-Host "1. Copy the public key to your server's ~/.ssh/authorized_keys" -ForegroundColor White
        Write-Host "2. Set environment variables for Ansible deployment:" -ForegroundColor White
        Write-Host "   - SERVER_IP: Your server IP address" -ForegroundColor White
        Write-Host "   - SERVER_USER: SSH username (default: root)" -ForegroundColor White
        Write-Host "   - SSH_KEY_PATH: $KeyPath" -ForegroundColor White
        Write-Host "   - GITHUB_REPOSITORY: Your GitHub repository URL" -ForegroundColor White
        
        Write-Host "`nSecurity note: Keys are stored in your user SSH directory for better security" -ForegroundColor Green
    } else {
        Write-Host "Failed to generate SSH key" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Error generating SSH key: $_" -ForegroundColor Red
    exit 1
} 