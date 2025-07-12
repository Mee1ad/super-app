#!/usr/bin/env python3
"""
Script to create the postgres database
"""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import settings
import databases

async def create_database():
    """Create the postgres database if it doesn't exist"""
    # Connect to the default postgres database
    postgres_url = f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/postgres"
    
    try:
        # Connect to postgres database
        database = databases.Database(postgres_url)
        await database.connect()
        
        # Check if postgres database exists
        result = await database.fetch_one(
            "SELECT 1 FROM pg_database WHERE datname = 'postgres'"
        )
        
        if result:
            print("✅ Database 'postgres' already exists")
        else:
            # Create the database
            await database.execute("CREATE DATABASE postgres")
            print("✅ Database 'postgres' created successfully")
        
        await database.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(create_database()) 