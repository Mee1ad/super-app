from typing import Optional, ClassVar
from datetime import datetime
from edgy import Model, fields, Manager

from db.base import UUIDBaseModel
from db.session import models_registry
import uuid


class Role(UUIDBaseModel):
    """Model for user roles"""
    objects: ClassVar[Manager] = Manager()

    id = fields.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        help_text="Unique identifier for the record"
    )
    name = fields.CharField(max_length=50, unique=True)
    description = fields.TextField(null=True)
    permissions = fields.JSONField(default=dict)  # Store permissions as JSON
    
    class Meta:
        tablename = "roles"
        registry = models_registry


class User(UUIDBaseModel):
    """User model with role-based access control"""
    objects: ClassVar[Manager] = Manager()
    
    email = fields.EmailField(unique=True, max_length=255)
    username = fields.CharField(max_length=255, unique=True)
    hashed_password = fields.CharField(max_length=255)
    is_active = fields.BooleanField(default=True)
    is_superuser = fields.BooleanField(default=False)
    role = fields.ForeignKey("Role", on_delete="SET NULL", null=True, related_name="users")
    created_at = fields.DateTimeField(auto_now_add=True)
    updated_at = fields.DateTimeField(auto_now=True)
    
    class Meta:
        tablename = "users"
        registry = models_registry
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission"""
        if self.is_superuser:
            return True
        
        if not self.role or not self.role.permissions:
            return False
        
        return permission in self.role.permissions
    
    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role"""
        if self.is_superuser:
            return True
        
        return self.role and self.role.name == role_name 