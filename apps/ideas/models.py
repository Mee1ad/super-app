# models for ideas app 
from typing import Optional, List
from uuid import UUID

from edgy import Model, fields

from db.base import BaseModel, utc_now
from db.session import models_registry


class Category(Model):
    """Category model for organizing ideas"""
    
    id = fields.CharField(primary_key=True, max_length=50)
    name = fields.CharField(max_length=100)
    emoji = fields.CharField(max_length=10)
    created_at = fields.DateTimeField(default=utc_now)
    updated_at = fields.DateTimeField(default=utc_now, auto_now=True)

    class Meta:
        tablename = "categories"
        registry = models_registry


class Idea(BaseModel):
    """Idea model for storing user ideas"""
    
    title = fields.CharField(max_length=255)
    description = fields.TextField(null=True, blank=True)
    category = fields.ForeignKey(
        "Category",
        on_delete="cascade",
        related_name="ideas"
    )
    tags = fields.JSONField(default=list)

    class Meta:
        tablename = "ideas"
        registry = models_registry 