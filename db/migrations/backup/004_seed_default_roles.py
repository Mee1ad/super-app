"""
Migration 004: Seed default roles
"""
from db.migrations.base import Migration
from db.session import database
from core.permissions import DEFAULT_ROLES
import json


class SeedDefaultRolesMigration(Migration):
    """Seed default roles in the system"""
    
    def get_version(self) -> str:
        return "004"
    
    def get_name(self) -> str:
        return "seed_default_roles"
    
    def get_description(self) -> str:
        return "Create default roles (admin, user, guest) with appropriate permissions"
    
    def get_dependencies(self) -> list[str]:
        return ["001"]
    
    async def up(self) -> None:
        """Create default roles"""
        for role_name, role_data in DEFAULT_ROLES.items():
            # Check if role already exists
            existing_role = await database.fetch_one(
                "SELECT id FROM roles WHERE name = :name",
                {"name": role_name}
            )
            
            if not existing_role:
                await database.execute("""
                    INSERT INTO roles (name, description, permissions)
                    VALUES (:name, :description, CAST(:permissions AS json))
                """, {
                    "name": role_name,
                    "description": role_data["description"],
                    "permissions": json.dumps(role_data["permissions"])
                })
    
    async def down(self) -> None:
        """Remove default roles"""
        for role_name in DEFAULT_ROLES.keys():
            await database.execute(
                "DELETE FROM roles WHERE name = :name",
                {"name": role_name}
            ) 