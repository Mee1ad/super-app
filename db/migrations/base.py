"""
Base migration class for incremental database migrations
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any
from databasez import Database

from db.session import database
from core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class MigrationInfo:
    """Information about a migration"""
    version: str
    name: str
    description: str
    dependencies: List[str]
    created_at: datetime
    applied_at: Optional[datetime] = None

class Migration(ABC):
    """Base migration class"""
    
    def __init__(self):
        self.database = database
    
    @abstractmethod
    def get_version(self) -> str:
        """Get migration version"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get migration name"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get migration description"""
        pass
    
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """Get migration dependencies"""
        pass
    
    @abstractmethod
    async def up(self) -> None:
        """Run migration up"""
        pass
    
    @abstractmethod
    async def down(self) -> None:
        """Run migration down"""
        pass
    
    async def is_applied(self) -> bool:
        """Check if migration is applied"""
        try:
            result = await self.database.fetch_one(
                "SELECT 1 FROM migrations WHERE version = :version",
                {"version": self.get_version()}
            )
            return result is not None
        except Exception:
            return False
    
    async def mark_applied(self) -> None:
        """Mark migration as applied"""
        await self.database.execute("""
            INSERT INTO migrations (version, name, description, dependencies, applied_at)
            VALUES (:version, :name, :description, :dependencies, :applied_at)
        """, {
            "version": self.get_version(),
            "name": self.get_name(),
            "description": self.get_description(),
            "dependencies": ",".join(self.get_dependencies()),
            "applied_at": datetime.utcnow()
        })
    
    async def mark_rolled_back(self) -> None:
        """Mark migration as rolled back"""
        await self.database.execute(
            "DELETE FROM migrations WHERE version = :version",
            {"version": self.get_version()}
        )

class MigrationManager:
    """Manages the execution of migrations"""
    
    def __init__(self):
        self.migrations: List[Migration] = []
        self._migration_table_created = False
    
    def register_migration(self, migration: Migration) -> None:
        """Register a migration"""
        self.migrations.append(migration)
        # Sort by version
        self.migrations.sort(key=lambda m: m.version)
    
    def _get_database_dialect(self) -> str:
        """Get database dialect for SQL compatibility"""
        if settings.is_testing:
            return "sqlite"
        return "postgresql"
    
    def _get_uuid_function(self) -> str:
        """Get UUID generation function based on dialect"""
        if self._get_database_dialect() == "sqlite":
            return "hex(randomblob(4)) || '-' || hex(randomblob(2)) || '-4' || substr(hex(randomblob(2)),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(hex(randomblob(2)),2) || '-' || hex(randomblob(6))"
        return "gen_random_uuid()"
    
    def _get_serial_type(self) -> str:
        """Get serial type based on dialect"""
        if self._get_database_dialect() == "sqlite":
            return "INTEGER PRIMARY KEY AUTOINCREMENT"
        return "SERIAL PRIMARY KEY"
    
    def _get_timestamp_default(self) -> str:
        """Get timestamp default based on dialect"""
        if self._get_database_dialect() == "sqlite":
            return "DATETIME('now')"
        return "CURRENT_TIMESTAMP"
    
    async def ensure_migration_table(self) -> None:
        """Ensure the migrations table exists with correct schema"""
        if self._migration_table_created:
            return
        
        try:
            dialect = self._get_database_dialect()
            
            if dialect == "sqlite":
                # SQLite doesn't have information_schema, check table existence differently
                result = await database.fetch_one("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='migrations'
                """)
                
                if result is None:
                    # Table doesn't exist, create it
                    logger.info("🔄 Migrations table doesn't exist, creating...")
                    await database.execute("""
                        CREATE TABLE migrations (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            version VARCHAR(50) UNIQUE NOT NULL,
                            name VARCHAR(255) NOT NULL,
                            description TEXT,
                            dependencies TEXT,
                            created_at DATETIME DEFAULT DATETIME('now'),
                            applied_at DATETIME DEFAULT DATETIME('now')
                        )
                    """)
                    
                    # Create indexes
                    await database.execute("CREATE INDEX idx_migrations_version ON migrations(version)")
                    await database.execute("CREATE INDEX idx_migrations_applied_at ON migrations(applied_at)")
                    
                    logger.info("✅ Migrations table created with correct schema")
                else:
                    # Check if table has correct schema by trying to query it
                    try:
                        await database.fetch_one("SELECT version FROM migrations LIMIT 1")
                        logger.info("✅ Migrations table exists with correct schema")
                    except Exception:
                        # Table exists but has wrong schema, recreate it
                        logger.info("🔄 Migrations table has wrong schema, recreating...")
                        await database.execute("DROP TABLE migrations")
                        await self.ensure_migration_table()
                        return
            else:
                # PostgreSQL - use information_schema
                result = await database.fetch_one("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'migrations' AND column_name = 'version'
                """)
                
                if result is None:
                    # Table doesn't exist or has wrong schema, recreate it
                    logger.info("🔄 Migrations table doesn't exist or has wrong schema, recreating...")
                    await database.execute("DROP TABLE IF EXISTS migrations")
                    
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
                    
                    # Create indexes
                    await database.execute("CREATE INDEX idx_migrations_version ON migrations(version)")
                    await database.execute("CREATE INDEX idx_migrations_applied_at ON migrations(applied_at)")
                    
                    logger.info("✅ Migrations table created with correct schema")
                else:
                    logger.info("✅ Migrations table exists with correct schema")
            
            self._migration_table_created = True
            
        except Exception as e:
            logger.error(f"Error ensuring migrations table: {e}")
            raise
    
    async def fix_table_schemas(self) -> None:
        """Fix common table schema issues"""
        try:
            dialect = self._get_database_dialect()
            
            # Fix moods table schema
            logger.info("🔄 Checking moods table schema...")
            
            if dialect == "sqlite":
                # Check if description column exists and remove it
                result = await database.fetch_one("""
                    SELECT name FROM pragma_table_info('moods') 
                    WHERE name = 'description'
                """)
                
                if result is not None:
                    logger.info("🔄 Removing description column from moods table...")
                    # SQLite doesn't support DROP COLUMN, need to recreate table
                    await database.execute("""
                        CREATE TABLE moods_new (
                            id TEXT PRIMARY KEY DEFAULT (hex(randomblob(4)) || '-' || hex(randomblob(2)) || '-4' || substr(hex(randomblob(2)),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(hex(randomblob(2)),2) || '-' || hex(randomblob(6))),
                            name VARCHAR(100) NOT NULL,
                            emoji VARCHAR(10),
                            color VARCHAR(20)
                        )
                    """)
                    
                    # Copy data (excluding description column)
                    await database.execute("""
                        INSERT INTO moods_new (id, name, emoji, color)
                        SELECT id, name, emoji, color FROM moods
                    """)
                    
                    await database.execute("DROP TABLE moods")
                    await database.execute("ALTER TABLE moods_new RENAME TO moods")
                    logger.info("✅ Description column removed from moods table")
                
                # Ensure required columns exist
                try:
                    await database.execute("ALTER TABLE moods ADD COLUMN emoji VARCHAR(10)")
                except Exception:
                    pass  # Column might already exist
                
                try:
                    await database.execute("ALTER TABLE moods ADD COLUMN color VARCHAR(20)")
                except Exception:
                    pass  # Column might already exist
            else:
                # PostgreSQL
                result = await database.fetch_one("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'moods' AND column_name = 'description'
                """)
                
                if result is not None:
                    logger.info("🔄 Removing description column from moods table...")
                    await database.execute("ALTER TABLE moods DROP COLUMN description")
                    logger.info("✅ Description column removed from moods table")
                
                # Ensure required columns exist
                await database.execute("ALTER TABLE moods ADD COLUMN IF NOT EXISTS emoji VARCHAR(10)")
                await database.execute("ALTER TABLE moods ADD COLUMN IF NOT EXISTS color VARCHAR(20)")
            
            logger.info("✅ Moods table schema fixed")
            
        except Exception as e:
            logger.warning(f"Warning: Could not fix table schemas: {e}")
            # Don't fail the migration process for schema fixes
    
    async def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions"""
        try:
            result = await database.fetch_all(
                "SELECT version FROM migrations ORDER BY version"
            )
            return [row[0] for row in result]
        except Exception as e:
            logger.error(f"Error getting applied migrations: {e}")
            return []
    
    async def check_dependencies(self, migration: Migration) -> bool:
        """Check if migration dependencies are satisfied"""
        applied_migrations = await self.get_applied_migrations()
        
        for dependency in migration.dependencies:
            if dependency not in applied_migrations:
                logger.error(f"❌ Migration {migration.version} depends on {dependency} which is not applied")
                return False
        
        return True
    
    async def migrate(self, target_version: Optional[str] = None) -> None:
        """Run migrations up to target version"""
        await self.ensure_migration_table()
        
        # Fix any schema issues before running migrations
        await self.fix_table_schemas()
        
        applied_migrations = await self.get_applied_migrations()
        pending_migrations = []
        
        for migration in self.migrations:
            if migration.version not in applied_migrations:
                if target_version and migration.version > target_version:
                    break
                pending_migrations.append(migration)
        
        if not pending_migrations:
            logger.info("✅ No pending migrations")
            return
        
        logger.info(f"🔄 Running {len(pending_migrations)} pending migrations...")
        
        for migration in pending_migrations:
            logger.info(f"🔄 Running migration {migration.version}: {migration.name}")
            
            # Check dependencies
            if not await self.check_dependencies(migration):
                raise Exception(f"Migration {migration.version} dependencies not satisfied")
            
            try:
                await migration.up()
                await migration.mark_applied()
                logger.info(f"✅ Migration {migration.version} completed successfully")
            except Exception as e:
                logger.error(f"❌ Migration {migration.version} failed: {e}")
                raise
    
    async def rollback(self, target_version: str) -> None:
        """Rollback migrations to target version"""
        await self.ensure_migration_table()
        
        applied_migrations = await self.get_applied_migrations()
        migrations_to_rollback = []
        
        # Find migrations to rollback (in reverse order)
        for migration in reversed(self.migrations):
            if migration.version in applied_migrations and migration.version > target_version:
                migrations_to_rollback.append(migration)
        
        if not migrations_to_rollback:
            logger.info("✅ No migrations to rollback")
            return
        
        logger.info(f"🔄 Rolling back {len(migrations_to_rollback)} migrations...")
        
        for migration in migrations_to_rollback:
            logger.info(f"🔄 Rolling back migration {migration.version}: {migration.name}")
            
            try:
                await migration.down()
                await migration.mark_rolled_back()
                logger.info(f"✅ Migration {migration.version} rolled back successfully")
            except Exception as e:
                logger.error(f"❌ Rollback of migration {migration.version} failed: {e}")
                raise
    
    async def status(self) -> Dict[str, Any]:
        """Get migration status"""
        await self.ensure_migration_table()
        
        applied_migrations = await self.get_applied_migrations()
        pending_migrations = []
        
        for migration in self.migrations:
            if migration.version not in applied_migrations:
                pending_migrations.append({
                    "version": migration.version,
                    "name": migration.name,
                    "description": migration.description,
                    "dependencies": migration.dependencies
                })
        
        return {
            "applied": applied_migrations,
            "pending": pending_migrations,
            "total": len(self.migrations),
            "applied_count": len(applied_migrations),
            "pending_count": len(pending_migrations)
        }


# Global migration manager instance
migration_manager = MigrationManager() 