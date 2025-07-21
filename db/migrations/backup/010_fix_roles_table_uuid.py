"""
Migration 010: Fix roles table UUID primary key
"""
import logging
from db.migrations.base import Migration
from db.session import database

logger = logging.getLogger(__name__)


class FixRolesTableUUIDMigration(Migration):
    """Fix roles table to use UUID primary key instead of text"""
    
    def get_version(self) -> str:
        return "010"
    
    def get_name(self) -> str:
        return "fix_roles_table_uuid"
    
    def get_description(self) -> str:
        return "Fix roles table primary key to use UUID instead of text to match foreign key constraint"
    
    def get_dependencies(self) -> list[str]:
        return ["001"]
    
    async def up(self) -> None:
        """Fix roles table primary key to use UUID"""
        dialect = self._get_database_dialect()
        
        if dialect == "postgresql":
            # Check if roles table exists and has text primary key
            result = await database.fetch_one("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name = 'roles' AND column_name = 'id'
            """)
            
            if result and result[0] == 'text':
                logger.info("🔄 Fixing roles table primary key from text to UUID...")
                
                # Create new roles table with UUID primary key
                await database.execute("""
                    CREATE TABLE roles_new (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        name VARCHAR(50) UNIQUE NOT NULL,
                        description TEXT,
                        permissions JSONB DEFAULT '{}',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Copy existing data, generating new UUIDs
                await database.execute("""
                    INSERT INTO roles_new (name, description, permissions, created_at, updated_at)
                    SELECT name, description, permissions, created_at, updated_at FROM roles
                """)
                
                # Drop old table and rename new one
                await database.execute("DROP TABLE roles")
                await database.execute("ALTER TABLE roles_new RENAME TO roles")
                
                logger.info("✅ Roles table primary key fixed to UUID")
            else:
                logger.info("✅ Roles table already has correct UUID primary key")
        else:
            # SQLite
            result = await database.fetch_one("""
                SELECT type FROM pragma_table_info('roles') 
                WHERE name = 'id'
            """)
            
            if result and result[0] == 'TEXT':
                logger.info("🔄 Fixing roles table primary key from TEXT to UUID...")
                
                # Create new roles table with UUID primary key
                await database.execute("""
                    CREATE TABLE roles_new (
                        id TEXT PRIMARY KEY DEFAULT (hex(randomblob(4)) || '-' || hex(randomblob(2)) || '-4' || substr(hex(randomblob(2)),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(hex(randomblob(2)),2) || '-' || hex(randomblob(6))),
                        name VARCHAR(50) UNIQUE NOT NULL,
                        description TEXT,
                        permissions TEXT DEFAULT '{}',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Copy existing data, generating new UUIDs
                await database.execute("""
                    INSERT INTO roles_new (name, description, permissions, created_at, updated_at)
                    SELECT name, description, permissions, created_at, updated_at FROM roles
                """)
                
                # Drop old table and rename new one
                await database.execute("DROP TABLE roles")
                await database.execute("ALTER TABLE roles_new RENAME TO roles")
                
                logger.info("✅ Roles table primary key fixed to UUID")
            else:
                logger.info("✅ Roles table already has correct UUID primary key")
    
    async def down(self) -> None:
        """Revert roles table primary key back to text (if needed)"""
        # This is a destructive operation, so we'll just log it
        logger.warning("⚠️  Down migration for roles table UUID fix is not implemented as it would be destructive")
    
    def _get_database_dialect(self) -> str:
        """Get database dialect"""
        url = str(database.url)
        if "postgresql" in url or "postgres" in url:
            return "postgresql"
        elif "sqlite" in url:
            return "sqlite"
        else:
            return "unknown" 