# PowerShell script to test remote database connection
# This script tests if you can connect to your production database remotely

param(
    [string]$ServerIP = "65.108.157.187",
    [string]$Database = "superapp",
    [string]$Username = "superapp",
    [string]$Password = "superapp123",
    [int]$Port = 5432
)

Write-Host "Testing remote database connection..." -ForegroundColor Green
Write-Host "Server: $ServerIP" -ForegroundColor Yellow
Write-Host "Database: $Database" -ForegroundColor Yellow
Write-Host "Username: $Username" -ForegroundColor Yellow
Write-Host "Port: $Port" -ForegroundColor Yellow
Write-Host ""

# Test 1: Check if port is open
Write-Host "1. Testing if port $Port is open..." -ForegroundColor Cyan
try {
    $tcpClient = New-Object System.Net.Sockets.TcpClient
    $tcpClient.ConnectAsync($ServerIP, $Port).Wait(5000) | Out-Null
    
    if ($tcpClient.Connected) {
        Write-Host "   ✅ Port $Port is open and accessible" -ForegroundColor Green
        $tcpClient.Close()
    } else {
        Write-Host "   ❌ Port $Port is not accessible" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ Port $Port is not accessible: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 2: Test PostgreSQL connection using psql (if available)
Write-Host "2. Testing PostgreSQL connection..." -ForegroundColor Cyan

# Check if psql is available in WSL
try {
    $psqlCommand = "PGPASSWORD='$Password' psql -h $ServerIP -p $Port -U $Username -d $Database -c 'SELECT version();'"
    $result = wsl bash -c $psqlCommand 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ PostgreSQL connection successful!" -ForegroundColor Green
        Write-Host "   Server version: $($result | Select-String 'PostgreSQL')" -ForegroundColor Gray
    } else {
        Write-Host "   ❌ PostgreSQL connection failed: $result" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ PostgreSQL connection test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 3: Test with Python (if available)
Write-Host "3. Testing with Python psycopg2..." -ForegroundColor Cyan

$pythonScript = @"
import psycopg2
import sys

try:
    conn = psycopg2.connect(
        host='$ServerIP',
        port=$Port,
        database='$Database',
        user='$Username',
        password='$Password'
    )
    print('✅ Python connection successful!')
    
    cursor = conn.cursor()
    cursor.execute('SELECT version();')
    version = cursor.fetchone()
    print(f'   Server version: {version[0]}')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'❌ Python connection failed: {e}')
    sys.exit(1)
"@

try {
    $result = python -c $pythonScript 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host $result -ForegroundColor Green
    } else {
        Write-Host $result -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ Python test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 4: Test with Node.js (if available)
Write-Host "4. Testing with Node.js..." -ForegroundColor Cyan

$nodeScript = @"
const { Client } = require('pg');

const client = new Client({
  host: '$ServerIP',
  port: $Port,
  database: '$Database',
  user: '$Username',
  password: '$Password',
});

async function testConnection() {
  try {
    await client.connect();
    console.log('✅ Node.js connection successful!');
    
    const result = await client.query('SELECT version();');
    console.log('   Server version:', result.rows[0].version);
    
    await client.end();
  } catch (err) {
    console.error('❌ Node.js connection failed:', err.message);
    process.exit(1);
  }
}

testConnection();
"@

try {
    $result = node -e $nodeScript 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host $result -ForegroundColor Green
    } else {
        Write-Host $result -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ Node.js test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Connection test completed!" -ForegroundColor Green
Write-Host ""
Write-Host "To connect manually:" -ForegroundColor Yellow
Write-Host "  psql -h $ServerIP -p $Port -U $Username -d $Database" -ForegroundColor Gray
Write-Host "  Password: $Password" -ForegroundColor Gray 