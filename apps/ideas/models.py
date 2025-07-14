# models for ideas app 
from typing import Optional, List, ClassVar
from uuid import UUID

from edgy import Model, fields, Manager

from db.base import BaseModel, utc_now
from db.session import models_registry


class Category(BaseModel):
    """Category model for organizing ideas"""
    objects: ClassVar[Manager] = Manager()
    
    id = fields.CharField(primary_key=True, max_length=50)
    name = fields.CharField(max_length=255)
    emoji = fields.CharField(max_length=10)
    created_at = fields.DateTimeField(default=utc_now)
    updated_at = fields.DateTimeField(default=utc_now, auto_now=True)

    class Meta:
        tablename = "categories"
        registry = models_registry


class Idea(BaseModel):
    """Idea model for storing user ideas"""
    objects: ClassVar[Manager] = Manager()
    
    user_id = fields.ForeignKey("User", on_delete="cascade", related_name="ideas")
    category = fields.ForeignKey("Category", on_delete="SET NULL", null=True, related_name="ideas")
    title = fields.CharField(max_length=255)
    description = fields.TextField(null=True, blank=True)
    is_archived = fields.BooleanField(default=False)
    created_at = fields.DateTimeField(auto_now_add=True)
    updated_at = fields.DateTimeField(auto_now=True)
    tags = fields.JSONField(default=list)

    class Meta:
        tablename = "ideas"
        registry = models_registry 