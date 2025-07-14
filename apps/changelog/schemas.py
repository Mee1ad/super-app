from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from .models import ChangeType


class ChangelogEntryBase(BaseModel):
    """Base schema for changelog entries"""
    version: str = Field(..., description="Semantic version (e.g., 1.2.0)")
    title: str = Field(..., description="Human-readable title for the change")
    description: str = Field(..., description="Detailed description of the change")
    change_type: ChangeType = Field(..., description="Type of change")
    is_breaking: bool = Field(default=False, description="Whether this is a breaking change")


class ChangelogEntryCreate(ChangelogEntryBase):
    """Schema for creating changelog entries"""
    commit_hash: str = Field(..., description="Git commit hash")
    commit_date: datetime = Field(..., description="Git commit date")
    commit_message: str = Field(..., description="Original git commit message")
    release_date: datetime = Field(..., description="Release date")


class ChangelogEntryResponse(ChangelogEntryBase):
    """Schema for changelog entry responses"""
    id: str
    commit_hash: str
    commit_date: datetime
    commit_message: str
    release_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        """Convert Edgy model to response schema with proper UUID handling"""
        data = {
            "id": str(obj.id),  # Convert UUID to string
            "version": obj.version,
            "title": obj.title,
            "description": obj.description,
            "change_type": obj.change_type,
            "is_breaking": obj.is_breaking,
            "commit_hash": obj.commit_hash,
            "commit_date": obj.commit_date,
            "commit_message": obj.commit_message,
            "release_date": obj.release_date,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at
        }
        return cls(**data)


class ChangelogViewCreate(BaseModel):
    """Schema for marking changelog entries as viewed"""
    entry_id: str = Field(..., description="Changelog entry ID")
    user_identifier: str = Field(..., description="User identifier (IP, user ID, or session)")


class ChangelogViewResponse(BaseModel):
    """Schema for changelog view responses"""
    id: str
    entry_id: str
    user_identifier: str
    viewed_at: datetime

    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        """Convert Edgy model to response schema with proper UUID handling"""
        data = {
            "id": str(obj.id),  # Convert UUID to string
            "entry_id": str(obj.entry),  # Convert UUID to string
            "user_identifier": obj.user_identifier,
            "viewed_at": obj.viewed_at
        }
        return cls(**data)


class ChangelogSummary(BaseModel):
    """Schema for changelog summary responses"""
    version: str
    release_date: datetime
    total_changes: int
    breaking_changes: int
    changes_by_type: dict[str, int]
    entries: List[ChangelogEntryResponse]


class ChangelogListResponse(BaseModel):
    """Schema for paginated changelog list responses"""
    entries: List[ChangelogEntryResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class UnreadChangelogResponse(BaseModel):
    """Schema for unread changelog entries"""
    unread_count: int
    latest_version: Optional[str] = None
    entries: List[ChangelogEntryResponse] 