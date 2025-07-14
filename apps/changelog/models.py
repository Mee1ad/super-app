from typing import Optional, ClassVar
from enum import Enum
from datetime import datetime

from edgy import Model, fields, Manager

from db.base import BaseModel
from db.session import models_registry


class ChangeType(str, Enum):
    """Types of changes for semantic versioning"""
    ADDED = "added"
    CHANGED = "changed"
    FIXED = "fixed"
    REMOVED = "removed"
    DEPRECATED = "deprecated"
    SECURITY = "security"


class ChangelogEntry(BaseModel):
    """Model for storing changelog entries"""
    objects: ClassVar[Manager] = Manager()
    
    version = fields.CharField(max_length=20)
    title = fields.CharField(max_length=255)
    description = fields.TextField()
    change_type = fields.ChoiceField(
        choices=ChangeType,
        max_length=20
    )
    commit_hash = fields.CharField(max_length=40)
    commit_date = fields.DateTimeField()
    commit_message = fields.TextField()
    is_breaking = fields.BooleanField(default=False)
    release_date = fields.DateTimeField()
    is_published = fields.BooleanField(default=False)  # Draft/Published status
    published_by = fields.ForeignKey("User", on_delete="SET NULL", null=True, related_name="published_changelogs")
    published_at = fields.DateTimeField(null=True)
    
    class Meta:
        tablename = "changelog_entries"
        registry = models_registry


class ChangelogView(BaseModel):
    """Model for tracking user views of changelog entries"""
    objects: ClassVar[Manager] = Manager()
    
    entry = fields.ForeignKey(
        "ChangelogEntry",
        on_delete="cascade",
        related_name="views"
    )
    user_identifier = fields.CharField(max_length=255)  # IP, user ID, or session
    viewed_at = fields.DateTimeField(auto_now=True)
    
    class Meta:
        tablename = "changelog_views"
        registry = models_registry


class LastProcessedCommit(BaseModel):
    """Model for tracking the last processed git commit"""
    objects: ClassVar[Manager] = Manager()
    
    commit_hash = fields.CharField(max_length=40, unique=True)
    processed_at = fields.DateTimeField(auto_now=True)
    
    class Meta:
        tablename = "last_processed_commits"
        registry = models_registry


# Ensure models are registered
ChangelogEntry.Meta.registry = models_registry
ChangelogView.Meta.registry = models_registry
LastProcessedCommit.Meta.registry = models_registry 