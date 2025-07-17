#!/usr/bin/env python3
"""
Fix migrations table structure
"""
import asyncio
import sys
import os
import platform

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.session import database

async def fix_migrations_table():
    """Fix the migrations table structure"""
    try:
        await database.connect()
        print("✅ Connected to database")
        
        # Drop the old migrations table
        print("🗑️  Dropping old migrations table...")
        await database.execute("DROP TABLE IF EXISTS migrations CASCADE")
        
        # Create the new migrations table with proper structure
        print("📝 Creating new migrations table...")
        await database.execute("""
            CREATE TABLE migrations (
                id SERIAL PRIMARY KEY,
                version VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                dependencies TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        print("✅ Migrations table created with proper structure")
        
        # Check existing tables to determine what migrations to mark as applied
        tables_result = await database.fetch_all("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name NOT IN ('migrations', 'alembic_version')
        """)
        
        existing_tables = [row[0] for row in tables_result]
        print(f"📋 Found existing tables: {', '.join(existing_tables)}")
        
        # Mark appropriate migrations as applied based on existing tables
        migrations_to_mark = []
        
        if existing_tables:
            # If we have any tables, mark initial schema as applied
            migrations_to_mark.append(("001", "initial_schema", "Create initial database schema"))
            
            # Check for user authentication fields
            try:
                result = await database.fetch_one("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
                    AND column_name = 'username'
                """)
                if result:
                    migrations_to_mark.append(("002", "add_user_authentication", "Add username, hashed_password, and is_superuser fields to users table"))
            except:
                pass
            
            # Check for changelog publishing fields
            try:
                result = await database.fetch_one("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'changelog_entries' 
                    AND column_name = 'is_published'
                """)
                if result:
                    migrations_to_mark.append(("003", "add_changelog_publishing", "Add is_published, published_by, and published_at fields to changelog_entries table"))
            except:
                pass
        
        # Mark migrations as applied
        for version, name, description in migrations_to_mark:
            await database.execute("""
                INSERT INTO migrations (version, name, description, dependencies, applied_at)
                VALUES (:version, :name, :description, :dependencies, CURRENT_TIMESTAMP)
            """, {
                "version": version,
                "name": name,
                "description": description,
                "dependencies": "" if version == "001" else "001"
            })
            print(f"✅ Marked migration {version} as applied")
        
        print("\n🎉 Migrations table fixed successfully!")
        
    except Exception as e:
        print(f"❌ Error fixing migrations table: {e}")
        raise
    finally:
        await database.disconnect()

if __name__ == "__main__":
    asyncio.run(fix_migrations_table()) 