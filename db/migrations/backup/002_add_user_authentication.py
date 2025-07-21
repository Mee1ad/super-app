"""
Migration 002: Add user authentication fields
"""
from db.migrations.base import Migration
from db.session import database


class AddUserAuthenticationMigration(Migration):
    """Add authentication fields to users table"""
    
    def get_version(self) -> str:
        return "002"
    
    def get_name(self) -> str:
        return "add_user_authentication"
    
    def get_description(self) -> str:
        return "Add username, hashed_password, and is_superuser fields to users table"
    
    def get_dependencies(self) -> list[str]:
        return ["001"]
    
    async def up(self) -> None:
        """Add authentication fields to users table"""
        # Add username column
        await database.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS username VARCHAR(255) UNIQUE
        """)
        
        # Add hashed_password column
        await database.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS hashed_password VARCHAR(255)
        """)
        
        # Add is_superuser column
        await database.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS is_superuser BOOLEAN DEFAULT FALSE
        """)
        
        # Add created_at and updated_at columns if they don't exist
        await database.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        """)
        
        await database.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        """)
        
        # Update existing users to have usernames
        result = await database.fetch_all(
            "SELECT id, email FROM users WHERE username IS NULL OR username = ''"
        )
        
        for row in result:
            user_id = str(row[0])
            email = str(row[1])
            username = email.split('@')[0]
            
            # Ensure username is unique
            base_username = username
            counter = 1
            while True:
                existing = await database.fetch_one(
                    "SELECT id FROM users WHERE username = :username AND id != :user_id",
                    {"username": username, "user_id": user_id}
                )
                if not existing:
                    break
                username = f"{base_username}{counter}"
                counter += 1
            
            await database.execute(
                "UPDATE users SET username = :username WHERE id = :user_id",
                {"username": username, "user_id": user_id}
            )
    
    async def down(self) -> None:
        """Remove authentication fields from users table"""
        # Remove columns in reverse order
        await database.execute("ALTER TABLE users DROP COLUMN IF EXISTS updated_at")
        await database.execute("ALTER TABLE users DROP COLUMN IF EXISTS created_at")
        await database.execute("ALTER TABLE users DROP COLUMN IF EXISTS is_superuser")
        await database.execute("ALTER TABLE users DROP COLUMN IF EXISTS hashed_password")
        await database.execute("ALTER TABLE users DROP COLUMN IF EXISTS username") 