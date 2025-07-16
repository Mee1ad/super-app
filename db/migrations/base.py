"""
Base migration class for incremental database migrations
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from db.session import database

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
    """Base class for all migrations"""
    
    def __init__(self):
        self.version = self.get_version()
        self.name = self.get_name()
        self.description = self.get_description()
        self.dependencies = self.get_dependencies()
    
    @abstractmethod
    def get_version(self) -> str:
        """Return the migration version (e.g., '001', '002')"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the migration name"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return the migration description"""
        pass
    
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """Return list of migration versions this migration depends on"""
        pass
    
    @abstractmethod
    async def up(self) -> None:
        """Apply the migration"""
        pass
    
    @abstractmethod
    async def down(self) -> None:
        """Rollback the migration"""
        pass
    
    async def is_applied(self) -> bool:
        """Check if this migration has been applied"""
        try:
            result = await database.fetch_one(
                "SELECT applied_at FROM migrations WHERE version = :version",
                {"version": self.version}
            )
            return result is not None
        except Exception as e:
            logger.error(f"Error checking migration status: {e}")
            return False
    
    async def mark_applied(self) -> None:
        """Mark this migration as applied"""
        try:
            await database.execute(
                """
                INSERT INTO migrations (version, name, description, dependencies, applied_at)
                VALUES (:version, :name, :description, :dependencies, :applied_at)
                """,
                {
                    "version": self.version,
                    "name": self.name,
                    "description": self.description,
                    "dependencies": ",".join(self.dependencies),
                    "applied_at": datetime.utcnow()
                }
            )
            logger.info(f"✅ Migration {self.version} marked as applied")
        except Exception as e:
            logger.error(f"Error marking migration as applied: {e}")
            raise
    
    async def mark_rolled_back(self) -> None:
        """Mark this migration as rolled back"""
        try:
            await database.execute(
                "DELETE FROM migrations WHERE version = :version",
                {"version": self.version}
            )
            logger.info(f"✅ Migration {self.version} marked as rolled back")
        except Exception as e:
            logger.error(f"Error marking migration as rolled back: {e}")
            raise


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
    
    async def ensure_migration_table(self) -> None:
        """Ensure the migrations table exists with correct schema"""
        if self._migration_table_created:
            return
        
        try:
            # Check if table exists and has correct schema
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