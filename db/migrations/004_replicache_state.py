"""
Migration 004: Add Replicache client state tables
"""
import logging
from db.migrations.base import Migration, migration_manager

logger = logging.getLogger(__name__)


class ReplicacheStateMigration(Migration):
    def get_version(self) -> str:
        return "004"

    def get_name(self) -> str:
        return "replicache_state"

    def get_description(self) -> str:
        return "Add tables to persist per-client lastMutationID and last-seen mapping"

    def get_dependencies(self) -> list[str]:
        return ["001"]

    async def up(self) -> None:
        dialect = migration_manager._get_database_dialect()
        timestamp_default = migration_manager._get_timestamp_default()

        # replicache_client_state
        if dialect == "sqlite":
            await self.database.execute(
                """
                CREATE TABLE IF NOT EXISTS replicache_client_state (
                    ns TEXT NOT NULL,
                    client_id TEXT NOT NULL,
                    last_mutation_id INTEGER NOT NULL DEFAULT 0,
                    updated_at DATETIME DEFAULT (DATETIME('now')),
                    PRIMARY KEY (ns, client_id)
                )
                """
            )
        else:
            await self.database.execute(
                f"""
                CREATE TABLE IF NOT EXISTS replicache_client_state (
                    ns TEXT NOT NULL,
                    client_id TEXT NOT NULL,
                    last_mutation_id BIGINT NOT NULL DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT {timestamp_default},
                    PRIMARY KEY (ns, client_id)
                )
                """
            )

        # replicache_last_seen
        if dialect == "sqlite":
            await self.database.execute(
                """
                CREATE TABLE IF NOT EXISTS replicache_last_seen (
                    ns TEXT NOT NULL,
                    profile_id TEXT NOT NULL,
                    client_group_id TEXT NOT NULL,
                    client_id TEXT NOT NULL,
                    updated_at DATETIME DEFAULT (DATETIME('now')),
                    PRIMARY KEY (ns, profile_id, client_group_id)
                )
                """
            )
        else:
            await self.database.execute(
                f"""
                CREATE TABLE IF NOT EXISTS replicache_last_seen (
                    ns TEXT NOT NULL,
                    profile_id TEXT NOT NULL,
                    client_group_id TEXT NOT NULL,
                    client_id TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT {timestamp_default},
                    PRIMARY KEY (ns, profile_id, client_group_id)
                )
                """
            )

        logger.info("✅ Replicache state tables ensured")

    async def down(self) -> None:
        await self.database.execute("DROP TABLE IF EXISTS replicache_last_seen")
        await self.database.execute("DROP TABLE IF EXISTS replicache_client_state")


# Register migration
from db.migrations.base import migration_manager

migration_manager.register_migration(ReplicacheStateMigration())

