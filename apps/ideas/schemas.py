# schemas for ideas app 
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


# Category Schemas
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the category")
    emoji: str = Field(..., min_length=1, max_length=10, description="Emoji icon for the category")


class CategoryCreate(CategoryBase):
    id: str = Field(..., min_length=1, max_length=50, description="Unique identifier for the category")


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="New name for the category")
    emoji: Optional[str] = Field(None, min_length=1, max_length=10, description="New emoji for the category")


class CategoryResponse(CategoryBase):
    id: str = Field(..., description="Unique identifier for the category")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


# Idea Schemas
class IdeaBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Title of the idea")
    description: Optional[str] = Field(None, description="Optional description of the idea")
    category: str = Field(..., description="Category ID for the idea")
    tags: List[str] = Field(default_factory=list, description="List of tags for the idea")


class IdeaCreate(IdeaBase):
    pass


class IdeaUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="New title for the idea")
    description: Optional[str] = Field(None, description="New description for the idea")
    category: Optional[str] = Field(None, description="New category ID for the idea")
    tags: Optional[List[str]] = Field(None, description="New tags for the idea")


class IdeaResponse(IdeaBase):
    id: UUID = Field(..., description="Unique identifier for the idea")
    user_id: UUID = Field(..., description="ID of the user who owns the idea")
    category_id: Optional[str] = Field(None, description="ID of the category")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    @classmethod
    def model_validate_from_orm(cls, obj):
        """Extract data from Edgy ORM model with proper category_id, category, and user_id handling"""
        data = {}
        for field_name in cls.model_fields.keys():
            if field_name == 'user_id':
                if hasattr(obj, 'user_id') and obj.user_id:
                    data['user_id'] = getattr(obj.user_id, 'id', obj.user_id)
                elif hasattr(obj, 'user_id'):
                    data['user_id'] = getattr(obj, 'user_id')
            elif field_name == 'category_id':
                # Special handling for category_id - extract string from ForeignKey field
                if hasattr(obj, 'category'):
                    category_value = getattr(obj, 'category')
                    if hasattr(category_value, 'id'):
                        data['category_id'] = category_value.id
                    else:
                        data['category_id'] = category_value
                elif hasattr(obj, 'category_id'):
                    data['category_id'] = getattr(obj, 'category_id')
            elif field_name == 'category':
                # Always set category as the category id (string)
                if hasattr(obj, 'category'):
                    category_value = getattr(obj, 'category')
                    if hasattr(category_value, 'id'):
                        data['category'] = category_value.id
                    else:
                        data['category'] = category_value
                elif hasattr(obj, 'category_id'):
                    data['category'] = getattr(obj, 'category_id')
            elif hasattr(obj, field_name):
                data[field_name] = getattr(obj, field_name)
        return cls.model_validate(data)


# Pagination Schemas
class PaginationMeta(BaseModel):
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


class IdeasResponse(BaseModel):
    ideas: List[IdeaResponse] = Field(..., description="Array of ideas")
    meta: PaginationMeta = Field(..., description="Pagination metadata")


class CategoriesResponse(BaseModel):
    categories: List[CategoryResponse] = Field(..., description="Array of categories")


# Error Response Schemas
class ErrorDetail(BaseModel):
    field: Optional[str] = Field(None, description="Field name that caused the error")
    issue: str = Field(..., description="Description of the validation issue")
    value: Optional[str] = Field(None, description="The value that caused the error")


class ErrorResponse(BaseModel):
    error: dict = Field(..., description="Error information")
    request_id: str = Field(..., description="Unique request identifier for support")
    timestamp: datetime = Field(..., description="Error timestamp")


class ValidationErrorResponse(ErrorResponse):
    error: dict = Field(..., description="Validation error details")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Validation failed",
                    "details": [
                        {
                            "field": "title",
                            "issue": "Field is required",
                            "value": None
                        }
                    ]
                },
                "request_id": "req_1234567890abcdef",
                "timestamp": "2024-12-01T10:00:00Z"
            }
        }
    )


class NotFoundErrorResponse(ErrorResponse):
    error: dict = Field(..., description="Not found error details")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": {
                    "code": "RESOURCE_NOT_FOUND",
                    "message": "Resource not found",
                    "details": {
                        "resource": "idea",
                        "id": "550e8400-e29b-41d4-a716-446655440000"
                    }
                },
                "request_id": "req_1234567890abcdef",
                "timestamp": "2024-12-01T10:00:00Z"
            }
        }
    ) 