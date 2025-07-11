# Base model logic for Edgy ORM 
from datetime import datetime, UTC
from typing import Optional
from uuid import uuid4

from edgy import Model, fields


def utc_now():
    """Get current UTC time - replacement for deprecated datetime.utcnow()"""
    return datetime.now(UTC)


class BaseModel(Model):
    """Base model with common fields"""
    
    id: fields.UUIDField = fields.UUIDField(primary_key=True, default=uuid4)
    created_at: fields.DateTimeField = fields.DateTimeField(default=utc_now)
    updated_at: fields.DateTimeField = fields.DateTimeField(default=utc_now, auto_now=True)

    class Meta:
        abstract = True 