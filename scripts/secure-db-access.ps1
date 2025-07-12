# Secure Database Access Script
# Uses SSH tunneling instead of direct remote access

param(
    [string]$ServerIP = "65.108.157.187",
    [string]$SSHUser = "postgres",
    [string]$SSHKey = "~/.ssh/super-app-backend",
    [int]$LocalPort = 5432,
    [int]$RemotePort = 5432
)

Write-Host "🔒 Secure Database Access via SSH Tunnel" -ForegroundColor Green
Write-Host ""

# Check if SSH key exists
Write-Host "1. Checking SSH key..." -ForegroundColor Cyan
try {
    $sshKeyPath = $SSHKey.Replace("~", $env:USERPROFILE)
    if (Test-Path $sshKeyPath) {
        Write-Host "   ✅ SSH key found: $sshKeyPath" -ForegroundColor Green
    } else {
        Write-Host "   ❌ SSH key not found: $sshKeyPath" -ForegroundColor Red
        Write-Host "   Please ensure your SSH key is properly configured." -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "   ❌ Error checking SSH key: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test SSH connection
Write-Host "2. Testing SSH connection..." -ForegroundColor Cyan
try {
    $sshTest = ssh -i $sshKeyPath -o ConnectTimeout=10 -o StrictHostKeyChecking=no ${SSHUser}@${ServerIP} "echo 'SSH connection successful'"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ SSH connection successful" -ForegroundColor Green
    } else {
        Write-Host "   ❌ SSH connection failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "   ❌ SSH connection error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Check if local port is available
Write-Host "3. Checking local port availability..." -ForegroundColor Cyan
try {
    $tcpClient = New-Object System.Net.Sockets.TcpClient
    $tcpClient.ConnectAsync("localhost", $LocalPort).Wait(2000) | Out-Null
    
    if ($tcpClient.Connected) {
        Write-Host "   ⚠️  Port $LocalPort is already in use" -ForegroundColor Yellow
        Write-Host "   Please close any existing connections or use a different port." -ForegroundColor Yellow
        $tcpClient.Close()
        exit 1
    } else {
        Write-Host "   ✅ Port $LocalPort is available" -ForegroundColor Green
    }
} catch {
    Write-Host "   ✅ Port $LocalPort is available" -ForegroundColor Green
}

Write-Host ""

# Create SSH tunnel
Write-Host "4. Creating SSH tunnel..." -ForegroundColor Cyan
Write-Host "   Local port: $LocalPort -> Remote: $ServerIP:$RemotePort" -ForegroundColor Gray
Write-Host "   Press Ctrl+C to stop the tunnel" -ForegroundColor Yellow
Write-Host ""

try {
    # Start SSH tunnel in background
    $sshCommand = "ssh -i $sshKeyPath -L ${LocalPort}:localhost:${RemotePort} -N ${SSHUser}@${ServerIP}"
    Write-Host "   Starting tunnel: $sshCommand" -ForegroundColor Gray
    Write-Host ""
    
    # Run SSH tunnel
    Invoke-Expression $sshCommand
    
} catch {
    Write-Host "   ❌ Failed to create SSH tunnel: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} 