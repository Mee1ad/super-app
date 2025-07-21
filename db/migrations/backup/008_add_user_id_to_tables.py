"""
Migration 008: Add user_id columns to user-related tables
"""
from db.migrations.base import Migration
from db.session import database


class AddUserIdToTablesMigration(Migration):
    """Add user_id columns to tables that need user association"""
    
    def get_version(self) -> str:
        return "008"
    
    def get_name(self) -> str:
        return "add_user_id_to_tables"
    
    def get_description(self) -> str:
        return "Add user_id foreign key columns to lists, tasks, shopping_items, diary_entries, food_entries, and ideas tables"
    
    def get_dependencies(self) -> list[str]:
        return ["002"]  # Depends on user authentication being added
    
    async def up(self) -> None:
        """Add user_id columns to user-related tables"""
        
        # Check if user_id column already exists in lists table
        lists_has_user_id = await self._column_exists("lists", "user_id")
        if not lists_has_user_id:
            await database.execute("""
                ALTER TABLE lists 
                ADD COLUMN user_id UUID REFERENCES users(id) ON DELETE CASCADE
            """)
            print("✅ Added user_id column to lists table")
        
        # Check if user_id column already exists in tasks table
        tasks_has_user_id = await self._column_exists("tasks", "user_id")
        if not tasks_has_user_id:
            await database.execute("""
                ALTER TABLE tasks 
                ADD COLUMN user_id UUID REFERENCES users(id) ON DELETE CASCADE
            """)
            print("✅ Added user_id column to tasks table")
        
        # Check if user_id column already exists in shopping_items table
        shopping_items_has_user_id = await self._column_exists("shopping_items", "user_id")
        if not shopping_items_has_user_id:
            await database.execute("""
                ALTER TABLE shopping_items 
                ADD COLUMN user_id UUID REFERENCES users(id) ON DELETE CASCADE
            """)
            print("✅ Added user_id column to shopping_items table")
        
        # Check if user_id column already exists in diary_entries table
        diary_entries_has_user_id = await self._column_exists("diary_entries", "user_id")
        if not diary_entries_has_user_id:
            await database.execute("""
                ALTER TABLE diary_entries 
                ADD COLUMN user_id UUID REFERENCES users(id) ON DELETE CASCADE
            """)
            print("✅ Added user_id column to diary_entries table")
        
        # Check if user_id column already exists in food_entries table
        food_entries_has_user_id = await self._column_exists("food_entries", "user_id")
        if not food_entries_has_user_id:
            await database.execute("""
                ALTER TABLE food_entries 
                ADD COLUMN user_id UUID REFERENCES users(id) ON DELETE CASCADE
            """)
            print("✅ Added user_id column to food_entries table")
        
        # Check if user_id column already exists in ideas table
        ideas_has_user_id = await self._column_exists("ideas", "user_id")
        if not ideas_has_user_id:
            await database.execute("""
                ALTER TABLE ideas 
                ADD COLUMN user_id UUID REFERENCES users(id) ON DELETE CASCADE
            """)
            print("✅ Added user_id column to ideas table")
        
        # Create indexes for better performance
        await self._create_indexes()
    
    async def down(self) -> None:
        """Remove user_id columns from tables"""
        # Drop indexes first
        await self._drop_indexes()
        
        # Remove user_id columns in reverse order
        await database.execute("ALTER TABLE ideas DROP COLUMN IF EXISTS user_id")
        await database.execute("ALTER TABLE food_entries DROP COLUMN IF EXISTS user_id")
        await database.execute("ALTER TABLE diary_entries DROP COLUMN IF EXISTS user_id")
        await database.execute("ALTER TABLE shopping_items DROP COLUMN IF EXISTS user_id")
        await database.execute("ALTER TABLE tasks DROP COLUMN IF EXISTS user_id")
        await database.execute("ALTER TABLE lists DROP COLUMN IF EXISTS user_id")
    
    async def _column_exists(self, table_name: str, column_name: str) -> bool:
        """Check if a column exists in a table"""
        try:
            # Try to get column information
            result = await database.fetch_one(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                AND column_name = '{column_name}'
            """)
            return result is not None
        except Exception:
            return False
    
    async def _create_indexes(self) -> None:
        """Create indexes for user_id columns for better performance"""
        try:
            await database.execute("CREATE INDEX IF NOT EXISTS idx_lists_user_id ON lists(user_id)")
            await database.execute("CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id)")
            await database.execute("CREATE INDEX IF NOT EXISTS idx_shopping_items_user_id ON shopping_items(user_id)")
            await database.execute("CREATE INDEX IF NOT EXISTS idx_diary_entries_user_id ON diary_entries(user_id)")
            await database.execute("CREATE INDEX IF NOT EXISTS idx_food_entries_user_id ON food_entries(user_id)")
            await database.execute("CREATE INDEX IF NOT EXISTS idx_ideas_user_id ON ideas(user_id)")
            print("✅ Created indexes for user_id columns")
        except Exception as e:
            print(f"⚠️ Warning: Could not create indexes: {e}")
    
    async def _drop_indexes(self) -> None:
        """Drop indexes for user_id columns"""
        try:
            await database.execute("DROP INDEX IF EXISTS idx_ideas_user_id")
            await database.execute("DROP INDEX IF EXISTS idx_food_entries_user_id")
            await database.execute("DROP INDEX IF EXISTS idx_diary_entries_user_id")
            await database.execute("DROP INDEX IF EXISTS idx_shopping_items_user_id")
            await database.execute("DROP INDEX IF EXISTS idx_tasks_user_id")
            await database.execute("DROP INDEX IF EXISTS idx_lists_user_id")
        except Exception:
            pass 