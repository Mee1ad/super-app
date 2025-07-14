from typing import Optional, ClassVar
from uuid import uuid4
from edgy import Model, fields, Manager
from db.session import models_registry
from db.base import BaseModel

class User(BaseModel):
    """User model for authentication"""
    objects: ClassVar[Manager] = Manager()
    id = fields.UUIDField(primary_key=True, default=uuid4)
    email = fields.CharField(max_length=255, unique=True, index=True)
    name = fields.CharField(max_length=255)
    picture = fields.CharField(max_length=500, null=True)
    google_id = fields.CharField(max_length=255, unique=True, null=True, index=True)
    is_active = fields.BooleanField(default=True)
    is_verified = fields.BooleanField(default=False)
    
    class Meta:
        tablename = "users"
        registry = models_registry 