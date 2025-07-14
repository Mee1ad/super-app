from typing import List, Optional
from uuid import UUID
from edgy import Model, fields
from db.base import BaseModel, utc_now
from db.session import models_registry

class MealType(Model):
    id = fields.CharField(primary_key=True, max_length=50)
    name = fields.CharField(max_length=100)
    emoji = fields.CharField(max_length=10)
    time = fields.CharField(max_length=5)  # HH:MM format
    created_at = fields.DateTimeField(default=utc_now)

    class Meta:
        tablename = "meal_types"
        registry = models_registry

class FoodEntry(BaseModel):
    user = fields.ForeignKey("User", on_delete="cascade", related_name="food_entries")
    name = fields.CharField(max_length=255)
    category = fields.CharField(max_length=20)  # 'planned' or 'eaten'
    meal_type = fields.ForeignKey("MealType", on_delete="cascade", related_name="food_entries")
    time = fields.CharField(max_length=5)  # HH:MM format
    date = fields.DateField(default=utc_now)
    comment = fields.TextField(null=True)
    image = fields.TextField(null=True)
    followed_plan = fields.BooleanField(null=True)
    symptoms = fields.JSONField(default=list)
    
    class Meta:
        tablename = "food_entries"
        registry = models_registry 