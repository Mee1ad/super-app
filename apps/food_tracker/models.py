from datetime import datetime
from typing import Optional
from edgy import Model, fields
from db.base import UUIDBaseModel, utc_now
from db.session import models_registry


class FoodEntry(UUIDBaseModel):
    """Food entry model for tracking food items"""
    
    user_id = fields.ForeignKey("User", on_delete="cascade", related_name="food_entries")
    name = fields.CharField(max_length=255)
    price = fields.FloatField(null=True)
    description = fields.TextField(null=True)
    image_url = fields.CharField(max_length=500, null=True)
    date = fields.DateTimeField(default=utc_now)
    
    class Meta:
        tablename = "food_entries"
        registry = models_registry 