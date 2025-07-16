#!/usr/bin/env python3
"""
Fix moods table schema
This script will fix the moods table to match the model definition
"""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.session import database
from core.config import settings

async def fix_moods_table():
    """Fix the moods table schema"""
    try:
        await database.connect()
        print("✅ Connected to database")
        
        # Read the SQL script
        sql_file = os.path.join(os.path.dirname(__file__), 'fix_moods_table.sql')
        with open(sql_file, 'r') as f:
            sql_script = f.read()
        
        # Execute the SQL script
        print("🔄 Fixing moods table schema...")
        await database.execute(sql_script)
        
        print("✅ Moods table schema fixed successfully")
        
        # Verify the table structure
        result = await database.fetch_all("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'moods' 
            ORDER BY ordinal_position
        """)
        
        print("\n📋 Current moods table structure:")
        for row in result:
            print(f"  - {row[0]}: {row[1]} ({'NULL' if row[2] == 'YES' else 'NOT NULL'})")
        
    except Exception as e:
        print(f"❌ Error fixing moods table: {e}")
        raise
    finally:
        await database.disconnect()

async def main():
    """Main function"""
    print("🚀 Starting moods table fix...")
    
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
        await fix_moods_table()
        print("🎉 Moods table fix completed successfully!")
        
    except Exception as e:
        print(f"💥 Moods table fix failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 