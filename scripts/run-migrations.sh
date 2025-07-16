#!/bin/bash

# Robust migration script for CI/CD
set -e

echo "🚀 Starting database migration process..."

# Function to check if database is ready
check_database() {
    echo "Checking database connectivity..."
    python -c "
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath('.'))))
from db.session import database
from core.config import settings

async def test_connection():
    try:
        await database.connect()
        print('✅ Database connection successful')
        await database.disconnect()
        return True
    except Exception as e:
        print(f'❌ Database connection failed: {e}')
        return False

result = asyncio.run(test_connection())
sys.exit(0 if result else 1)
"
}

# Function to run migrations
run_migrations() {
    echo "Running database migrations..."
    python db/migrate_incremental.py migrate
}

# Wait for database to be ready
echo "Waiting for database to be ready..."
for i in {1..30}; do
    if check_database; then
        echo "✅ Database is ready"
        break
    elif [ $i -eq 30 ]; then
        echo "❌ Database failed to become ready within 30 attempts"
        exit 1
    else
        echo "Database not ready yet. Waiting... ($i/30)"
        sleep 2
    fi
done

# Run migrations with retry
echo "Running migrations with retry mechanism..."
for i in {1..5}; do
    if run_migrations; then
        echo "✅ Migrations completed successfully"
        exit 0
    else
        echo "❌ Migration attempt $i failed"
        if [ $i -eq 5 ]; then
            echo "❌ All migration attempts failed"
            exit 1
        fi
        echo "Retrying in 5s..."
        sleep 5
    fi
done 