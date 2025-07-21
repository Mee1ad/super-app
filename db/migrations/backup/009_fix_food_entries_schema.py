"""
Migration 009: Fix food entries schema to match frontend expectations
"""
from db.migrations.base import Migration, migration_manager


class FixFoodEntriesSchemaMigration(Migration):
    """Fix food entries table schema to match frontend expectations"""
    
    def get_version(self) -> str:
        return "009"
    
    def get_name(self) -> str:
        return "fix_food_entries_schema"
    
    def get_description(self) -> str:
        return "Fix food entries table schema to match frontend expectations by renaming title to name and adding missing columns"
    
    def get_dependencies(self) -> list[str]:
        return ["008"]
    
    async def _column_exists(self, table: str, column: str) -> bool:
        """Check if a column exists in a table"""
        try:
            result = await self.database.fetch_one(f"""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_name = '{table}' AND column_name = '{column}'
            """)
            return result[0] > 0 if result else False
        except Exception:
            return False
    
    async def up(self) -> None:
        """Fix food entries schema"""
        database = self.database
        
        # Check if name column already exists
        name_exists = await self._column_exists("food_entries", "name")
        if not name_exists:
            # Rename title to name
            await database.execute("ALTER TABLE food_entries RENAME COLUMN title TO name")
            print("✅ Renamed title column to name in food_entries table")
        
        # Check if category column exists
        category_exists = await self._column_exists("food_entries", "category")
        if not category_exists:
            # Add category column with default value
            await database.execute("""
                ALTER TABLE food_entries 
                ADD COLUMN category VARCHAR(20) NOT NULL DEFAULT 'eaten'
            """)
            print("✅ Added category column to food_entries table")
        
        # Check if time column exists
        time_exists = await self._column_exists("food_entries", "time")
        if not time_exists:
            # Add time column with default value
            await database.execute("""
                ALTER TABLE food_entries 
                ADD COLUMN time VARCHAR(5) NOT NULL DEFAULT '12:00'
            """)
            print("✅ Added time column to food_entries table")
        
        # Update existing records to have proper category and time values
        await database.execute("""
            UPDATE food_entries 
            SET category = 'eaten', time = '12:00' 
            WHERE category IS NULL OR time IS NULL
        """)
        print("✅ Updated existing records with default values")
    
    async def down(self) -> None:
        """Revert the changes"""
        database = self.database
        
        # Remove time column
        time_exists = await self._column_exists("food_entries", "time")
        if time_exists:
            await database.execute("ALTER TABLE food_entries DROP COLUMN time")
            print("✅ Removed time column from food_entries table")
        
        # Remove category column
        category_exists = await self._column_exists("food_entries", "category")
        if category_exists:
            await database.execute("ALTER TABLE food_entries DROP COLUMN category")
            print("✅ Removed category column from food_entries table")
        
        # Rename name back to title
        name_exists = await self._column_exists("food_entries", "name")
        if name_exists:
            await database.execute("ALTER TABLE food_entries RENAME COLUMN name TO title")
            print("✅ Renamed name column back to title in food_entries table")


# Register the migration
migration_manager.register_migration(FixFoodEntriesSchemaMigration()) 