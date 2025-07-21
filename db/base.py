# Base model logic for Edgy ORM 
from datetime import datetime, UTC
from typing import Optional
import uuid

from edgy import Model, fields


def utc_now():
    """Get current UTC time - replacement for deprecated datetime.utcnow()"""
    return datetime.now(UTC)


class BaseModel(Model):
    """Base model with common fields"""
    
    created_at: fields.DateTimeField = fields.DateTimeField(default=utc_now)
    updated_at: fields.DateTimeField = fields.DateTimeField(default=utc_now, auto_now=True)

    class Meta:
        abstract = True


class UUIDBaseModel(BaseModel):
    """Base model with UUID primary key following best practices"""
    
    id: fields.UUIDField = fields.UUIDField(
        primary_key=True, 
        default=uuid.uuid4,
        help_text="Unique identifier for the record"
    )

    class Meta:
        abstract = True 