"""
Migration 005: Add last_mutation_id columns to todo tables for delta pulls
"""
from db.migrations.base import Migration, migration_manager


class TodoRowVersionsMigration(Migration):
    def get_version(self) -> str:
        return "005"

    def get_name(self) -> str:
        return "todo_row_versions"

    def get_description(self) -> str:
        return "Add last_mutation_id BIGINT to lists and tasks to enable delta syncs"

    def get_dependencies(self) -> list[str]:
        return ["001"]

    async def up(self) -> None:
        dialect = migration_manager._get_database_dialect()
        if dialect == "sqlite":
            await self.database.execute("ALTER TABLE lists ADD COLUMN last_mutation_id INTEGER NOT NULL DEFAULT 0")
            await self.database.execute("ALTER TABLE tasks ADD COLUMN last_mutation_id INTEGER NOT NULL DEFAULT 0")
        else:
            await self.database.execute("ALTER TABLE lists ADD COLUMN IF NOT EXISTS last_mutation_id BIGINT NOT NULL DEFAULT 0")
            await self.database.execute("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS last_mutation_id BIGINT NOT NULL DEFAULT 0")

    async def down(self) -> None:
        # Optional: skip column drops for safety
        pass


from db.migrations.base import migration_manager
migration_manager.register_migration(TodoRowVersionsMigration())

