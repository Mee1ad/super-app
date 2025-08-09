"""
Migration 006: Add cv sequencing and tombstones for Replicache (todo namespace)
"""
import logging
from db.migrations.base import Migration, migration_manager

logger = logging.getLogger(__name__)


class ReplicacheCvAndTombstonesMigration(Migration):
    def get_version(self) -> str:
        return "006"

    def get_name(self) -> str:
        return "replicache_cv_and_tombstones"

    def get_description(self) -> str:
        return (
            "Add cv columns on todo tables, per-namespace cv sequence/state, and tombstones"
        )

    def get_dependencies(self) -> list[str]:
        # Depends on initial schema and replicache state tables
        return ["001", "004"]

    async def up(self) -> None:
        dialect = migration_manager._get_database_dialect()
        timestamp_default = migration_manager._get_timestamp_default()

        # Create generic cv state table for all dialects (used especially on SQLite)
        if dialect == "sqlite":
            await self.database.execute(
                """
                CREATE TABLE IF NOT EXISTS replicache_cv (
                    ns TEXT PRIMARY KEY,
                    value INTEGER NOT NULL DEFAULT 0
                )
                """
            )
        else:
            await self.database.execute(
                """
                CREATE TABLE IF NOT EXISTS replicache_cv (
                    ns TEXT PRIMARY KEY,
                    value BIGINT NOT NULL DEFAULT 0
                )
                """
            )

        # PostgreSQL: also create native sequence for todo namespace
        if dialect != "sqlite":
            await self.database.execute("CREATE SEQUENCE IF NOT EXISTS todo_cv_seq")

        # Add cv columns to lists, tasks, and shopping_items
        if dialect == "sqlite":
            # SQLite: ALTER TABLE ADD COLUMN fails if exists; ignore errors
            try:
                await self.database.execute(
                    "ALTER TABLE lists ADD COLUMN cv INTEGER NOT NULL DEFAULT 0"
                )
            except Exception:
                pass
            try:
                await self.database.execute(
                    "ALTER TABLE tasks ADD COLUMN cv INTEGER NOT NULL DEFAULT 0"
                )
            except Exception:
                pass
            try:
                await self.database.execute(
                    "ALTER TABLE shopping_items ADD COLUMN cv INTEGER NOT NULL DEFAULT 0"
                )
            except Exception:
                pass
        else:
            await self.database.execute(
                "ALTER TABLE lists ADD COLUMN IF NOT EXISTS cv BIGINT NOT NULL DEFAULT 0"
            )
            await self.database.execute(
                "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS cv BIGINT NOT NULL DEFAULT 0"
            )
            await self.database.execute(
                "ALTER TABLE shopping_items ADD COLUMN IF NOT EXISTS cv BIGINT NOT NULL DEFAULT 0"
            )

        # Create tombstones table for todo namespace
        if dialect == "sqlite":
            await self.database.execute(
                """
                CREATE TABLE IF NOT EXISTS todo_tombstones (
                    user_id TEXT NOT NULL,
                    key TEXT NOT NULL,
                    cv INTEGER NOT NULL,
                    created_at DATETIME NOT NULL DEFAULT (DATETIME('now')),
                    PRIMARY KEY (user_id, key)
                )
                """
            )
        else:
            await self.database.execute(
                f"""
                CREATE TABLE IF NOT EXISTS todo_tombstones (
                    user_id UUID NOT NULL,
                    key TEXT NOT NULL,
                    cv BIGINT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT {timestamp_default},
                    PRIMARY KEY (user_id, key)
                )
                """
            )

        # Indexes for fast delta queries
        await self.database.execute(
            "CREATE INDEX IF NOT EXISTS lists_user_cv_idx ON lists (user_id, cv)"
        )
        await self.database.execute(
            "CREATE INDEX IF NOT EXISTS tasks_user_cv_idx ON tasks (user_id, cv)"
        )
        await self.database.execute(
            "CREATE INDEX IF NOT EXISTS shopping_items_user_cv_idx ON shopping_items (user_id, cv)"
        )
        await self.database.execute(
            "CREATE INDEX IF NOT EXISTS todo_tombstones_user_cv_idx ON todo_tombstones (user_id, cv)"
        )

        logger.info("✅ Replicache cv and tombstones migration applied")

    async def down(self) -> None:
        # Be conservative; don't drop columns. Only drop tables created by this migration
        await self.database.execute("DROP TABLE IF EXISTS todo_tombstones")
        await self.database.execute("DROP TABLE IF EXISTS replicache_cv")
        # Do not drop sequences or remove columns to avoid data loss


# Register migration
migration_manager.register_migration(ReplicacheCvAndTombstonesMigration())


