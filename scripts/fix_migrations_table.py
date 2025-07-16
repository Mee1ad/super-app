#!/usr/bin/env python3
"""
Fix migrations table schema
This script will recreate the migrations table with the correct schema
"""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.session import database
from core.config import settings

async def fix_migrations_table():
    """Fix the migrations table schema"""
    try:
        await database.connect()
        print("✅ Connected to database")
        
        # Read the SQL script
        sql_file = os.path.join(os.path.dirname(__file__), 'fix-migrations-table.sql')
        with open(sql_file, 'r') as f:
            sql_script = f.read()
        
        # Execute the SQL script
        print("🔄 Fixing migrations table schema...")
        await database.execute(sql_script)
        
        print("✅ Migrations table schema fixed successfully")
        
        # Verify the table structure
        result = await database.fetch_all("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'migrations' 
            ORDER BY ordinal_position
        """)
        
        print("\n📋 Current migrations table structure:")
        for row in result:
            print(f"  - {row[0]}: {row[1]} ({'NULL' if row[2] == 'YES' else 'NOT NULL'})")
        
    except Exception as e:
        print(f"❌ Error fixing migrations table: {e}")
        raise
    finally:
        await database.disconnect()

async def main():
    """Main function"""
    print("🚀 Starting migrations table fix...")
    
    # Debug configuration details
    print("=== Database Configuration Debug ===")
    print(f"Environment: {settings.environment}")
    print(f"Is Production: {settings.is_production}")
    print(f"DB Host: {settings.db_host}")
    print(f"DB Port: {settings.db_port}")
    print(f"DB Name: {settings.db_name}")
    print(f"DB User: {settings.db_user}")
    print(f"Database URL: {settings.get_database_url()}")
    print("=== End Debug ===")
    
    try:
        await fix_migrations_table()
        print("🎉 Migrations table fix completed successfully!")
        
    except Exception as e:
        print(f"💥 Migrations table fix failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 