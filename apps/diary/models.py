from typing import Optional, ClassVar
from uuid import UUID
from datetime import date
from edgy import Model, fields, Manager
from db.base import BaseModel, utc_now
from db.session import models_registry

class Mood(BaseModel):
    objects: ClassVar[Manager] = Manager()
    id = fields.UUIDField(primary_key=True)
    name = fields.CharField(max_length=100)
    emoji = fields.CharField(max_length=10)
    color = fields.CharField(max_length=20)

    class Meta:
        tablename = "moods"
        registry = models_registry

class DiaryEntry(BaseModel):
    objects: ClassVar[Manager] = Manager()
    user_id = fields.ForeignKey("User", on_delete="cascade", related_name="diary_entries")
    mood = fields.ForeignKey("Mood", on_delete="SET NULL", null=True, related_name="diary_entries")
    title = fields.CharField(max_length=255)
    content = fields.TextField()
    date = fields.DateField()
    created_at = fields.DateTimeField(auto_now_add=True)
    updated_at = fields.DateTimeField(auto_now=True)
    
    class Meta:
        tablename = "diary_entries"
        registry = models_registry 