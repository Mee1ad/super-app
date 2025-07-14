from typing import Optional, ClassVar
from uuid import UUID
from edgy import Model, fields, Manager
from db.base import BaseModel, utc_now
from db.session import models_registry

class MealType(BaseModel):
    objects: ClassVar[Manager] = Manager()
    id = fields.UUIDField(primary_key=True)
    name = fields.CharField(max_length=100)
    emoji = fields.CharField(max_length=10)
    time = fields.CharField(max_length=10)
    created_at = fields.DateTimeField(default=utc_now)

    class Meta:
        tablename = "meal_types"
        registry = models_registry

class FoodEntry(BaseModel):
    objects: ClassVar[Manager] = Manager()
    user_id = fields.ForeignKey("User", on_delete="cascade", related_name="food_entries")
    meal_type = fields.ForeignKey("MealType", on_delete="SET NULL", null=True, related_name="food_entries")
    title = fields.CharField(max_length=255)
    calories = fields.IntegerField(null=True)
    date = fields.DateField()
    created_at = fields.DateTimeField(auto_now_add=True)
    updated_at = fields.DateTimeField(auto_now=True)
    comment = fields.TextField(null=True)
    image = fields.TextField(null=True)
    followed_plan = fields.BooleanField(null=True)
    symptoms = fields.JSONField(default=list)
    
    class Meta:
        tablename = "food_entries"
        registry = models_registry 