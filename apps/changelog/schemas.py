from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

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


class ChangelogEntryResponse(BaseModel):
    """Response schema for changelog entries"""
    id: str
    version: str
    title: str
    description: str
    change_type: ChangeType
    commit_hash: str
    commit_date: datetime
    commit_message: str
    is_breaking: bool
    release_date: datetime
    is_published: bool
    published_by: Optional[str] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_orm(cls, obj):
        """Convert Edgy model to response schema with proper UUID and User handling"""
        data = {
            "id": str(obj.id),  # Convert UUID to string
            "version": obj.version,
            "title": obj.title,
            "description": obj.description,
            "change_type": obj.change_type,
            "commit_hash": obj.commit_hash,
            "commit_date": obj.commit_date,
            "commit_message": obj.commit_message,
            "is_breaking": obj.is_breaking,
            "release_date": obj.release_date,
            "is_published": obj.is_published,
            "published_by": str(obj.published_by.id) if obj.published_by else None,  # Convert User to string ID
            "published_at": obj.published_at,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at
        }
        return cls(**data)


class ChangelogViewCreate(BaseModel):
    """Schema for creating changelog views"""
    entry_id: str
    user_identifier: str


class ChangelogViewResponse(BaseModel):
    """Schema for changelog view responses"""
    id: str
    entry_id: str
    user_identifier: str
    viewed_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
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
    """Response schema for changelog summary"""
    version: str
    release_date: Optional[datetime]
    total_changes: int
    breaking_changes: int
    changes_by_type: Dict[str, int]
    entries: List[ChangelogEntryResponse]


class ChangelogListResponse(BaseModel):
    """Response schema for paginated changelog lists"""
    entries: List[ChangelogEntryResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class UnreadChangelogResponse(BaseModel):
    """Response schema for unread changelog entries"""
    entries: List[ChangelogEntryResponse]
    total: int


class ChangelogPublishRequest(BaseModel):
    """Request schema for publishing changelog entries"""
    entry_id: str


class ChangelogPublishResponse(BaseModel):
    """Response schema for publishing changelog entries"""
    success: bool
    message: str
    entry_id: str


class AnonymousChangelogStatus(BaseModel):
    """Response schema for anonymous changelog status"""
    should_show: bool
    latest_version: Optional[str]
    user_version: Optional[str]
    has_new_content: bool


class AnonymousChangelogResponse(BaseModel):
    """Response schema for anonymous changelog entries"""
    entries: List[ChangelogEntryResponse]
    total: int
    latest_version: Optional[str]
    user_version: Optional[str]
    has_new_content: bool
    reason: Optional[str] = Field(None, description="Reason for the response (new_user, user_already_seen, no_latest_version, error)")


class AnonymousViewRequest(BaseModel):
    """Request schema for marking anonymous changelog as viewed"""
    ip_address: str
    user_agent: str = Field(alias="userAgent")
    
    model_config = ConfigDict(populate_by_name=True) 