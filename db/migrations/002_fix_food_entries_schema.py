"""
Migration 002: Fix food_entries table schema
Aligns the database table with the FoodEntry model
"""
import logging
from db.migrations.base import Migration, migration_manager

logger = logging.getLogger(__name__)


class FixFoodEntriesSchemaMigration(Migration):
    """Fix food_entries table schema to match the model"""
    
    def get_version(self) -> str:
        return "002"
    
    def get_name(self) -> str:
        return "fix_food_entries_schema"
    
    def get_description(self) -> str:
        return "Fix food_entries table schema to match the FoodEntry model"
    
    def get_dependencies(self) -> list[str]:
        return ["001"]
    
    async def _column_exists(self, table: str, column: str) -> bool:
        """Check if a column exists in a table"""
        result = await self.database.fetch_one("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = :table AND column_name = :column
            )
        """, {"table": table, "column": column})
        return result[0] if result else False
    
    async def up(self) -> None:
        """Fix food_entries table schema"""
        logger.info("🔄 Fixing food_entries table schema...")
        
        # Add missing price column
        price_exists = await self._column_exists("food_entries", "price")
        if not price_exists:
            await self.database.execute("ALTER TABLE food_entries ADD COLUMN price DECIMAL(10,2) NULL")
            logger.info("✅ Added price column to food_entries table")
        
        # Add missing description column (rename comment if it exists)
        description_exists = await self._column_exists("food_entries", "description")
        comment_exists = await self._column_exists("food_entries", "comment")
        
        if not description_exists and comment_exists:
            # Rename comment to description
            await self.database.execute("ALTER TABLE food_entries RENAME COLUMN comment TO description")
            logger.info("✅ Renamed comment column to description in food_entries table")
        elif not description_exists:
            # Add description column
            await self.database.execute("ALTER TABLE food_entries ADD COLUMN description TEXT NULL")
            logger.info("✅ Added description column to food_entries table")
        
        # Add missing image_url column (rename image if it exists)
        image_url_exists = await self._column_exists("food_entries", "image_url")
        image_exists = await self._column_exists("food_entries", "image")
        
        if not image_url_exists and image_exists:
            # Rename image to image_url
            await self.database.execute("ALTER TABLE food_entries RENAME COLUMN image TO image_url")
            logger.info("✅ Renamed image column to image_url in food_entries table")
        elif not image_url_exists:
            # Add image_url column
            await self.database.execute("ALTER TABLE food_entries ADD COLUMN image_url VARCHAR(500) NULL")
            logger.info("✅ Added image_url column to food_entries table")
        
        # Remove columns that are not in the model
        columns_to_remove = ['meal_type', 'category', 'time', 'calories', 'followed_plan', 'symptoms']
        
        for column in columns_to_remove:
            if await self._column_exists("food_entries", column):
                await self.database.execute(f"ALTER TABLE food_entries DROP COLUMN {column}")
                logger.info(f"✅ Removed {column} column from food_entries table")
        
        # Change date column type from date to timestamp if needed
        # Check current date column type
        result = await self.database.fetch_one("""
            SELECT data_type FROM information_schema.columns 
            WHERE table_name = 'food_entries' AND column_name = 'date'
        """)
        
        if result and result[0] == 'date':
            # Convert date column to timestamp
            await self.database.execute("ALTER TABLE food_entries ALTER COLUMN date TYPE TIMESTAMP WITH TIME ZONE")
            logger.info("✅ Changed date column type to TIMESTAMP WITH TIME ZONE")
        
        logger.info("✅ Food entries schema fixed successfully")
    
    async def down(self) -> None:
        """Revert food_entries table schema changes"""
        logger.info("🔄 Reverting food_entries table schema...")
        
        # This is a destructive migration, so we'll just log the reversal
        logger.warning("⚠️ This migration cannot be safely reversed as it removes columns")
        logger.info("✅ Food entries schema reversion logged") 