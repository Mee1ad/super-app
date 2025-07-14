from datetime import datetime, date
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

class MoodBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    emoji: str = Field(..., min_length=1, max_length=10)
    color: str = Field(..., min_length=1, max_length=50)

class MoodCreate(MoodBase):
    id: str = Field(..., min_length=1, max_length=50)

class MoodResponse(MoodBase):
    id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

class DiaryEntryBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(...)
    mood: str = Field(..., description="Mood ID for the entry")
    date: Optional[date] = None
    images: List[str] = Field(default_factory=list)
    model_config = ConfigDict(arbitrary_types_allowed=True)

class DiaryEntryCreate(DiaryEntryBase):
    pass

class DiaryEntryUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None)
    mood: Optional[str] = Field(None)
    date: Optional[date] = None
    images: Optional[List[str]] = Field(None)
    model_config = ConfigDict(arbitrary_types_allowed=True)

class DiaryEntryResponse(DiaryEntryBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
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
            elif field_name == 'mood':
                if hasattr(obj, 'mood'):
                    mood_value = getattr(obj, 'mood')
                    if hasattr(mood_value, 'id'):
                        data['mood'] = mood_value.id
                    else:
                        data['mood'] = mood_value
                elif hasattr(obj, 'mood_id'):
                    data['mood'] = getattr(obj, 'mood_id')
            elif hasattr(obj, field_name):
                data[field_name] = getattr(obj, field_name)
        return cls.model_validate(data)

class DiaryEntriesResponse(BaseModel):
    entries: List[DiaryEntryResponse]
    meta: dict
    model_config = ConfigDict(arbitrary_types_allowed=True)

class MoodsResponse(BaseModel):
    moods: List[MoodResponse]
    model_config = ConfigDict(arbitrary_types_allowed=True) 