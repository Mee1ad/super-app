# Windows PowerShell script to run Ansible deployment from WSL
# This script follows the user's preference to run Ansible from WSL

Write-Host "Running Ansible deployment from WSL..." -ForegroundColor Green

# Check if WSL is available
try {
    wsl --version | Out-Null
} catch {
    Write-Host "Error: WSL is not available. Please install WSL first." -ForegroundColor Red
    exit 1
}

# Run the Ansible deployment command in WSL
$wslCommand = "cd /mnt/e/Dev/super-app-backend && ./run-ansible-deploy.sh"

Write-Host "Executing: $wslCommand" -ForegroundColor Yellow
wsl bash -c $wslCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host "Ansible deployment completed successfully!" -ForegroundColor Green
} else {
    Write-Host "Ansible deployment failed with exit code: $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
} 