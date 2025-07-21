"""Migration: Unified changelog tracking

This migration updates the changelog_views table to use unified IP + User-Agent tracking
for all users (both anonymous and authenticated).
"""

from db.migrations.base import Migration
from db.session import database


class Migration007(Migration):
    """Unified changelog tracking"""
    
    def get_version(self) -> str:
        return "007"
    
    def get_name(self) -> str:
        return "unified_changelog_tracking"
    
    def get_description(self) -> str:
        return "Update changelog_views table for unified IP + User-Agent tracking"
    
    def get_dependencies(self) -> list[str]:
        return ["001"]
    
    async def up(self) -> None:
        """Update changelog_views table for unified tracking"""
        # Drop the old changelog_views table if it exists
        await database.execute("DROP TABLE IF EXISTS changelog_views CASCADE;")
        
        # Create new unified changelog_views table
        await database.execute("""
            CREATE TABLE IF NOT EXISTS changelog_views (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                hashed_ip VARCHAR(64) NOT NULL,
                hashed_user_agent VARCHAR(64) NOT NULL,
                latest_version_seen VARCHAR(20) NOT NULL,
                first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                view_count INTEGER DEFAULT 1,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(hashed_ip, hashed_user_agent)
            );
        """)
        
        # Create indexes for performance
        await database.execute("""
            CREATE INDEX IF NOT EXISTS idx_changelog_views_hashed_ip 
            ON changelog_views(hashed_ip);
        """)
        
        await database.execute("""
            CREATE INDEX IF NOT EXISTS idx_changelog_views_hashed_ua 
            ON changelog_views(hashed_user_agent);
        """)
        
        # Create composite index for the unique constraint
        await database.execute("""
            CREATE INDEX IF NOT EXISTS idx_changelog_views_composite 
            ON changelog_views(hashed_ip, hashed_user_agent);
        """)
        
        # Create index for analytics queries
        await database.execute("""
            CREATE INDEX IF NOT EXISTS idx_changelog_views_last_seen 
            ON changelog_views(last_seen);
        """)

    async def down(self) -> None:
        """Rollback to old changelog_views table"""
        # Drop the new table
        await database.execute("DROP TABLE IF EXISTS changelog_views CASCADE;")
        
        # Recreate the old table structure (if needed)
        await database.execute("""
            CREATE TABLE IF NOT EXISTS changelog_views (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                entry UUID REFERENCES changelog_entries(id) ON DELETE CASCADE,
                user_identifier VARCHAR(255) NOT NULL,
                viewed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """) 