from datetime import datetime, date as date_type
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

class MealTypeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    emoji: str = Field(..., min_length=1, max_length=10)
    time: str = Field(..., pattern=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')  # HH:MM format

class MealTypeCreate(MealTypeBase):
    id: UUID

class MealTypeResponse(MealTypeBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

class FoodEntryBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., pattern=r'^(planned|eaten)$')
    meal_type_id: UUID
    time: str = Field(..., pattern=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')  # HH:MM format
    date: date_type
    comment: Optional[str] = Field(None)
    image: Optional[str] = Field(None)
    followed_plan: Optional[bool] = Field(None)
    symptoms: List[str] = Field(default_factory=list)
    model_config = ConfigDict(arbitrary_types_allowed=True)

class FoodEntryCreate(FoodEntryBase):
    pass

class FoodEntryUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, pattern=r'^(planned|eaten)$')
    meal_type_id: Optional[UUID] = Field(None)
    time: Optional[str] = Field(None, pattern=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    date: Optional[date_type] = Field(None)
    comment: Optional[str] = Field(None)
    image: Optional[str] = Field(None)
    followed_plan: Optional[bool] = Field(None)
    symptoms: Optional[List[str]] = Field(None)
    model_config = ConfigDict(arbitrary_types_allowed=True)

class FoodEntryResponse(FoodEntryBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    meal_type: Optional[MealTypeResponse] = None
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, arbitrary_types_allowed=True)
    
    @classmethod
    def model_validate_from_orm(cls, obj):
        data = {}
        for field_name in cls.model_fields.keys():
            if field_name == 'user_id':
                if hasattr(obj, 'user_id') and obj.user_id:
                    data['user_id'] = getattr(obj.user_id, 'id', obj.user_id)
                elif hasattr(obj, 'user_id'):
                    data['user_id'] = getattr(obj, 'user_id')
            elif field_name == 'meal_type':
                if hasattr(obj, 'meal_type') and obj.meal_type:
                    data['meal_type'] = MealTypeResponse.model_validate(obj.meal_type)
                else:
                    data['meal_type'] = None
            elif hasattr(obj, field_name):
                data[field_name] = getattr(obj, field_name)
        return cls.model_validate(data)

class FoodEntriesResponse(BaseModel):
    entries: List[FoodEntryResponse]
    meta: dict
    model_config = ConfigDict(arbitrary_types_allowed=True)

class MealTypesResponse(BaseModel):
    meal_types: List[MealTypeResponse]
    model_config = ConfigDict(arbitrary_types_allowed=True)

class FoodSummaryResponse(BaseModel):
    planned_count: int
    eaten_count: int
    followed_plan_count: int
    off_plan_count: int
    model_config = ConfigDict(arbitrary_types_allowed=True)

class DaySummaryResponse(BaseModel):
    date: date_type
    planned_count: int
    eaten_count: int
    followed_plan: bool
    model_config = ConfigDict(arbitrary_types_allowed=True)

class CalendarResponse(BaseModel):
    days: List[DaySummaryResponse]
    model_config = ConfigDict(arbitrary_types_allowed=True) 