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
    type: ListType
    title: str = Field(..., min_length=1, max_length=255)
    variant: Variant = Variant.DEFAULT


class ListCreate(ListBase):
    pass


class ListUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    variant: Optional[Variant] = None


class ListResponse(ListBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Task Schemas
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    checked: bool = False
    variant: Variant = Variant.DEFAULT
    position: int = 0


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    checked: Optional[bool] = None
    variant: Optional[Variant] = None
    position: Optional[int] = None


class TaskResponse(TaskBase):
    id: UUID
    list_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Shopping Item Schemas
class ShoppingItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    url: Optional[str] = Field(None, max_length=500)
    price: Optional[str] = Field(None, max_length=50)
    source: Optional[str] = Field(None, max_length=255)
    checked: bool = False
    variant: Variant = Variant.DEFAULT
    position: int = 0


class ShoppingItemCreate(ShoppingItemBase):
    pass


class ShoppingItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    url: Optional[str] = Field(None, max_length=500)
    price: Optional[str] = Field(None, max_length=50)
    source: Optional[str] = Field(None, max_length=255)
    checked: Optional[bool] = None
    variant: Optional[Variant] = None
    position: Optional[int] = None


class ShoppingItemResponse(ShoppingItemBase):
    id: UUID
    list_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Reorder Schemas
class ReorderRequest(BaseModel):
    item_ids: List[UUID] = Field(..., min_length=1)


# Search Schemas
class SearchResponse(BaseModel):
    lists: List[ListResponse]
    tasks: List[TaskResponse]
    shopping_items: List[ShoppingItemResponse]


# List with Items Schemas
class ListWithTasksResponse(ListResponse):
    tasks: List[TaskResponse] = []


class ListWithShoppingItemsResponse(ListResponse):
    shopping_items: List[ShoppingItemResponse] = [] 