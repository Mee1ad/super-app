"""
Migration 003: Add changelog publishing fields
"""
from db.migrations.base import Migration
from db.session import database


class AddChangelogPublishingMigration(Migration):
    """Add publishing fields to changelog entries"""
    
    def get_version(self) -> str:
        return "003"
    
    def get_name(self) -> str:
        return "add_changelog_publishing"
    
    def get_description(self) -> str:
        return "Add is_published, published_by, and published_at fields to changelog_entries table"
    
    def get_dependencies(self) -> list[str]:
        return ["001"]
    
    async def up(self) -> None:
        """Add publishing fields to changelog_entries table"""
        # Add is_published column
        await database.execute("""
            ALTER TABLE changelog_entries 
            ADD COLUMN IF NOT EXISTS is_published BOOLEAN DEFAULT FALSE
        """)
        
        # Add published_by column
        await database.execute("""
            ALTER TABLE changelog_entries 
            ADD COLUMN IF NOT EXISTS published_by UUID REFERENCES users(id) ON DELETE SET NULL
        """)
        
        # Add published_at column
        await database.execute("""
            ALTER TABLE changelog_entries 
            ADD COLUMN IF NOT EXISTS published_at TIMESTAMP
        """)
    
    async def down(self) -> None:
        """Remove publishing fields from changelog_entries table"""
        await database.execute("ALTER TABLE changelog_entries DROP COLUMN IF EXISTS published_at")
        await database.execute("ALTER TABLE changelog_entries DROP COLUMN IF EXISTS published_by")
        await database.execute("ALTER TABLE changelog_entries DROP COLUMN IF EXISTS is_published") 