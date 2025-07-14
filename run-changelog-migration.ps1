# Changelog Migration Script
Write-Host "🚀 Running changelog migration..." -ForegroundColor Green

# Check if Python is available
try {
    python --version | Out-Null
} catch {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Run the migration
Write-Host "📝 Creating changelog tables..." -ForegroundColor Yellow
python db/migrate_changelog.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Changelog migration completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Next steps:" -ForegroundColor Cyan
    Write-Host "1. Add your DEEPSEEK_API_KEY to .env file" -ForegroundColor White
    Write-Host "2. Test the functionality: python test_changelog.py" -ForegroundColor White
    Write-Host "3. Process initial commits: curl -X POST http://localhost:8000/api/v1/changelog/process-commits" -ForegroundColor White
} else {
    Write-Host "❌ Changelog migration failed!" -ForegroundColor Red
    exit 1
} 