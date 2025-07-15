"""Migration: Add anonymous changelog views table

This migration adds a new table to track anonymous user changelog views
with privacy protection using separate hashed IP and user agent fields.
"""

from db.migrations.base import Migration
from db.session import database


class Migration006(Migration):
    """Add anonymous changelog views table"""
    
    def get_version(self) -> str:
        return "006"
    
    def get_name(self) -> str:
        return "add_anonymous_changelog_views"
    
    def get_description(self) -> str:
        return "Add anonymous changelog views table with privacy protection"
    
    def get_dependencies(self) -> list[str]:
        return ["001"]
    
    async def up(self) -> None:
        """Create anonymous_changelog_views table"""
        await database.execute("""
            CREATE TABLE IF NOT EXISTS anonymous_changelog_views (
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
        
        # Create index for faster lookups
        await database.execute("""
            CREATE INDEX IF NOT EXISTS idx_anonymous_changelog_views_hashed_ip 
            ON anonymous_changelog_views(hashed_ip);
        """)
        
        await database.execute("""
            CREATE INDEX IF NOT EXISTS idx_anonymous_changelog_views_hashed_ua 
            ON anonymous_changelog_views(hashed_user_agent);
        """)
        
        # Create composite index for the unique constraint
        await database.execute("""
            CREATE INDEX IF NOT EXISTS idx_anonymous_changelog_views_composite 
            ON anonymous_changelog_views(hashed_ip, hashed_user_agent);
        """)
        
        # Create index for analytics queries
        await database.execute("""
            CREATE INDEX IF NOT EXISTS idx_anonymous_changelog_views_last_seen 
            ON anonymous_changelog_views(last_seen);
        """)

    async def down(self) -> None:
        """Drop anonymous_changelog_views table"""
        await database.execute("DROP TABLE IF EXISTS anonymous_changelog_views CASCADE;") 