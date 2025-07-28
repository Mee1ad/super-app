import logging
from typing import Any
from edgy import Migration

logger = logging.getLogger(__name__)


class IncreaseImageUrlLengthMigration(Migration):
    """Migration to increase image_url field length for base64 data support"""
    
    async def up(self) -> None:
        """Increase image_url field length"""
        logger.info("🔄 Increasing image_url field length...")
        
        # Check if image_url column exists
        result = await self.database.fetch_one("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'food_entries' AND column_name = 'image_url'
        """)
        
        if result:
            # Update the column to allow longer strings
            await self.database.execute("ALTER TABLE food_entries ALTER COLUMN image_url TYPE VARCHAR(10000)")
            logger.info("✅ Increased image_url field length to 10000 characters")
        else:
            logger.warning("⚠️ image_url column not found, skipping migration")
        
        logger.info("✅ Image URL length migration completed successfully")
    
    async def down(self) -> None:
        """Revert image_url field length"""
        logger.info("🔄 Reverting image_url field length...")
        
        # Check if image_url column exists
        result = await self.database.fetch_one("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'food_entries' AND column_name = 'image_url'
        """)
        
        if result:
            # Revert the column back to 500 characters
            await self.database.execute("ALTER TABLE food_entries ALTER COLUMN image_url TYPE VARCHAR(500)")
            logger.info("✅ Reverted image_url field length to 500 characters")
        else:
            logger.warning("⚠️ image_url column not found, skipping rollback")
        
        logger.info("✅ Image URL length rollback completed successfully") 