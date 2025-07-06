# Base model logic for Edgy ORM 
from datetime import datetime
from typing import Optional
from uuid import uuid4

from edgy import Model, fields


class BaseModel(Model):
    """Base model with common fields"""
    
    id: fields.UUIDField = fields.UUIDField(primary_key=True, default=uuid4)
    created_at: fields.DateTimeField = fields.DateTimeField(default=datetime.utcnow)
    updated_at: fields.DateTimeField = fields.DateTimeField(default=datetime.utcnow, auto_now=True)

    class Meta:
        abstract = True 