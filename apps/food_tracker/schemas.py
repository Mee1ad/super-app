from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class FoodEntryBase(BaseModel):
    """Base food entry schema"""
    name: str = Field(..., min_length=1, max_length=255, description="Food item name")
    price: Optional[float] = Field(None, ge=0, description="Price of the food item")
    description: Optional[str] = Field(None, max_length=1000, description="Description of the food item")
    image_url: Optional[str] = Field(None, max_length=500, description="URL to food image")
    date: datetime = Field(default_factory=datetime.now, description="Date of the food entry")


class FoodEntryCreate(FoodEntryBase):
    """Schema for creating a new food entry"""
    pass


class FoodEntryUpdate(BaseModel):
    """Schema for updating a food entry"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    price: Optional[float] = Field(None, ge=0)
    description: Optional[str] = Field(None, max_length=1000)
    image_url: Optional[str] = Field(None, max_length=500)
    date: Optional[datetime] = None


class FoodEntryResponse(FoodEntryBase):
    """Schema for food entry response"""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FoodEntriesResponse(BaseModel):
    """Schema for multiple food entries response"""
    entries: List[FoodEntryResponse]
    total: int
    page: int
    limit: int
    pages: int


class FoodSummaryResponse(BaseModel):
    """Schema for food summary response"""
    total_entries: int
    total_spent: float
    average_price: float
    entries_by_date: dict[str, int]  # date string -> count 