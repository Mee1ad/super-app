from typing import List, Optional
from uuid import UUID
from edgy import Model, fields
from db.base import BaseModel, utc_now
from db.session import models_registry

class Mood(Model):
    id = fields.CharField(primary_key=True, max_length=50)
    name = fields.CharField(max_length=100)
    emoji = fields.CharField(max_length=10)
    color = fields.CharField(max_length=50)
    created_at = fields.DateTimeField(default=utc_now)

    class Meta:
        tablename = "moods"
        registry = models_registry

class DiaryEntry(BaseModel):
    title = fields.CharField(max_length=255)
    content = fields.TextField()
    mood = fields.ForeignKey("Mood", on_delete="cascade", related_name="entries")
    date = fields.DateField(default=utc_now)
    images = fields.JSONField(default=list)
    
    class Meta:
        tablename = "diary_entries"
        registry = models_registry 