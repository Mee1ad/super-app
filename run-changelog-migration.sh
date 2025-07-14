#!/bin/bash

# Changelog Migration Script
echo "🚀 Running changelog migration..."

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed or not in PATH"
    exit 1
fi

# Run the migration
echo "📝 Creating changelog tables..."
python db/migrate_changelog.py

if [ $? -eq 0 ]; then
    echo "✅ Changelog migration completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Add your DEEPSEEK_API_KEY to .env file"
    echo "2. Test the functionality: python test_changelog.py"
    echo "3. Process initial commits: curl -X POST http://localhost:8000/api/v1/changelog/process-commits"
else
    echo "❌ Changelog migration failed!"
    exit 1
fi 