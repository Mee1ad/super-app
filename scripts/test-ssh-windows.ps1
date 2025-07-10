# Simple SSH Test for Windows
# Tests if SSH tunneling will work on your system

param(
    [string]$ServerIP = "65.108.157.187",
    [string]$SSHUser = "superapp",
    [string]$SSHKey = "~/.ssh/super-app-backend"
)

Write-Host "🔍 Testing SSH Setup for Windows" -ForegroundColor Green
Write-Host ""

# Test 1: Check if SSH is available
Write-Host "1. Checking SSH availability..." -ForegroundColor Cyan
try {
    $sshVersion = ssh -V 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ SSH client available: $sshVersion" -ForegroundColor Green
    } else {
        Write-Host "   ❌ SSH client not found" -ForegroundColor Red
        Write-Host "   Install OpenSSH from Windows Features or use Git Bash" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "   ❌ SSH client not available" -ForegroundColor Red
    Write-Host "   Try: Settings > Apps > Optional Features > Add Feature > OpenSSH Client" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Test 2: Check SSH key
Write-Host "2. Checking SSH key..." -ForegroundColor Cyan
$sshKeyPath = $SSHKey.Replace("~", $env:USERPROFILE)
if (Test-Path $sshKeyPath) {
    Write-Host "   ✅ SSH key found: $sshKeyPath" -ForegroundColor Green
} else {
    Write-Host "   ❌ SSH key not found: $sshKeyPath" -ForegroundColor Red
    Write-Host "   Please ensure your SSH key is properly configured." -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Test 3: Test SSH connection
Write-Host "3. Testing SSH connection..." -ForegroundColor Cyan
try {
    $sshTest = ssh -i $sshKeyPath -o ConnectTimeout=10 -o StrictHostKeyChecking=no ${SSHUser}@${ServerIP} "echo 'SSH connection successful'"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ SSH connection successful" -ForegroundColor Green
    } else {
        Write-Host "   ❌ SSH connection failed" -ForegroundColor Red
        Write-Host "   Check your SSH key and server connectivity" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "   ❌ SSH connection error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 4: Check if port 5432 is available locally
Write-Host "4. Checking local port availability..." -ForegroundColor Cyan
try {
    $tcpClient = New-Object System.Net.Sockets.TcpClient
    $tcpClient.ConnectAsync("localhost", 5432).Wait(2000) | Out-Null
    
    if ($tcpClient.Connected) {
        Write-Host "   ⚠️  Port 5432 is already in use" -ForegroundColor Yellow
        Write-Host "   Close any existing connections or use a different port" -ForegroundColor Yellow
        $tcpClient.Close()
    } else {
        Write-Host "   ✅ Port 5432 is available for tunneling" -ForegroundColor Green
    }
} catch {
    Write-Host "   ✅ Port 5432 is available for tunneling" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎉 SSH setup is ready for tunneling!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Run: .\scripts\secure-db-access.ps1" -ForegroundColor Gray
Write-Host "2. In another terminal: psql -h localhost -p 5432 -U superapp -d superapp" -ForegroundColor Gray
Write-Host "3. Or use DBeaver/pgAdmin with SSH tunneling" -ForegroundColor Gray 