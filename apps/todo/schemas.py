# schemas for todo app 
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class ListType(str, Enum):
    TASK = "task"
    SHOPPING = "shopping"


class Variant(str, Enum):
    DEFAULT = "default"
    OUTLINED = "outlined"
    FILLED = "filled"


# List Schemas
class ListBase(BaseModel):
    type: ListType = Field(..., description="Type of list - either 'task' for todo items or 'shopping' for shopping items")
    title: str = Field(..., min_length=1, max_length=255, description="Title of the list")
    variant: Variant = Field(Variant.DEFAULT, description="Visual variant for UI styling")


class ListCreate(ListBase):
    pass


class ListUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="New title for the list")
    variant: Optional[Variant] = Field(None, description="New visual variant for the list")


class ListResponse(ListBase):
    id: UUID = Field(..., description="Unique identifier for the list")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


# Task Schemas
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Title of the task")
    description: Optional[str] = Field(None, description="Optional description of the task")
    checked: bool = Field(False, description="Whether the task is completed")
    variant: Variant = Field(Variant.DEFAULT, description="Visual variant for UI styling")
    position: int = Field(0, description="Position in the list for ordering")


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    list_id: Optional[UUID] = Field(None, description="ID of the parent list (optional, for update)")
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="New title for the task")
    description: Optional[str] = Field(None, description="New description for the task")
    checked: Optional[bool] = Field(None, description="New completion status")
    variant: Optional[Variant] = Field(None, description="New visual variant")
    position: Optional[int] = Field(None, description="New position in the list")


class TaskResponse(TaskBase):
    id: UUID = Field(..., description="Unique identifier for the task")
    list_id: UUID = Field(..., description="ID of the parent list")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    @classmethod
    def from_orm(cls, obj):
        data = obj.dict() if hasattr(obj, 'dict') else obj
        # If list_id is present directly, use it
        if 'list_id' in data and data['list_id']:
            pass  # already present
        elif 'list' in data and isinstance(data['list'], dict) and 'id' in data['list']:
            data['list_id'] = data['list']['id']
        elif 'list' in data and hasattr(data['list'], 'id'):
            data['list_id'] = data['list'].id
        elif hasattr(obj, 'list_id'):
            data['list_id'] = getattr(obj, 'list_id')
        return cls(**data)


# Shopping Item Schemas
class ShoppingItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Title of the shopping item")
    url: Optional[str] = Field(None, max_length=500, description="Optional URL to the product")
    price: Optional[str] = Field(None, max_length=50, description="Price of the item")
    source: Optional[str] = Field(None, max_length=255, description="Source/store for the item")
    checked: bool = Field(False, description="Whether the item is purchased")
    variant: Variant = Field(Variant.DEFAULT, description="Visual variant for UI styling")
    position: int = Field(0, description="Position in the list for ordering")


class ShoppingItemCreate(ShoppingItemBase):
    pass


class ShoppingItemUpdate(BaseModel):
    list_id: Optional[UUID] = Field(None, description="ID of the parent list (optional, for update)")
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="New title for the shopping item")
    url: Optional[str] = Field(None, max_length=500, description="New URL for the item")
    price: Optional[str] = Field(None, max_length=50, description="New price for the item")
    source: Optional[str] = Field(None, max_length=255, description="New source for the item")
    checked: Optional[bool] = Field(None, description="New purchase status")
    variant: Optional[Variant] = Field(None, description="New visual variant")
    position: Optional[int] = Field(None, description="New position in the list")


class ShoppingItemResponse(ShoppingItemBase):
    id: UUID = Field(..., description="Unique identifier for the shopping item")
    list_id: UUID = Field(..., description="ID of the parent list")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    @classmethod
    def from_orm(cls, obj):
        data = obj.dict() if hasattr(obj, 'dict') else obj
        # If list_id is present directly, use it
        if 'list_id' in data and data['list_id']:
            pass  # already present
        elif 'list' in data and isinstance(data['list'], dict) and 'id' in data['list']:
            data['list_id'] = data['list']['id']
        elif 'list' in data and hasattr(data['list'], 'id'):
            data['list_id'] = data['list'].id
        elif hasattr(obj, 'list_id'):
            data['list_id'] = getattr(obj, 'list_id')
        return cls(**data)


# Reorder Schemas
class ReorderRequest(BaseModel):
    item_ids: List[UUID] = Field(..., min_length=1, description="Array of item IDs in the desired order")


# Search Schemas
class SearchResponse(BaseModel):
    lists: List[ListResponse] = Field(..., description="Matching lists")
    tasks: List[TaskResponse] = Field(..., description="Matching tasks")
    shopping_items: List[ShoppingItemResponse] = Field(..., description="Matching shopping items")


# List with Items Schemas
class ListWithTasksResponse(ListResponse):
    tasks: List[TaskResponse] = []


class ListWithShoppingItemsResponse(ListResponse):
    shopping_items: List[ShoppingItemResponse] = []


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
                        "resource": "list",
                        "id": "550e8400-e29b-41d4-a716-446655440000"
                    }
                },
                "request_id": "req_1234567890abcdef",
                "timestamp": "2024-12-01T10:00:00Z"
            }
        }
    )


class AuthErrorResponse(ErrorResponse):
    error: dict = Field(..., description="Authentication error details")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": {
                    "code": "AUTH_REQUIRED",
                    "message": "Authentication required",
                    "details": {
                        "header": "Authorization",
                        "format": "Bearer <token>"
                    }
                },
                "request_id": "req_1234567890abcdef",
                "timestamp": "2024-12-01T10:00:00Z"
            }
        }
    )


class RateLimitErrorResponse(ErrorResponse):
    error: dict = Field(..., description="Rate limit error details")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Rate limit exceeded",
                    "details": {
                        "limit": 1000,
                        "reset_time": "2024-12-01T11:00:00Z",
                        "retry_after": 3600
                    }
                },
                "request_id": "req_1234567890abcdef",
                "timestamp": "2024-12-01T10:00:00Z"
            }
        }
    ) 