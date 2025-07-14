# models for todo app 
from typing import Optional
from enum import Enum

from edgy import Model, fields

from db.base import BaseModel
from db.session import models_registry


class ListType(str, Enum):
    TASK = "task"
    SHOPPING = "shopping"


class Variant(str, Enum):
    DEFAULT = "default"
    OUTLINED = "outlined"
    FILLED = "filled"


class List(BaseModel):
    """List model for organizing tasks and shopping items"""
    
    user_id = fields.ForeignKey("User", on_delete="cascade", related_name="lists")
    type: fields.ChoiceField = fields.ChoiceField(
        choices=ListType,
        max_length=20
    )
    title: fields.CharField = fields.CharField(max_length=255)
    variant: fields.ChoiceField = fields.ChoiceField(
        choices=Variant,
        default=Variant.DEFAULT,
        max_length=20
    )

    class Meta:
        tablename = "lists"
        registry = models_registry


class Task(BaseModel):
    """Task model for todo items"""
    
    user_id = fields.ForeignKey("User", on_delete="cascade", related_name="tasks")
    list: fields.ForeignKey = fields.ForeignKey(
        "List",
        on_delete="cascade",
        related_name="tasks"
    )
    title: fields.CharField = fields.CharField(max_length=255)
    description: fields.TextField = fields.TextField(null=True, blank=True)
    checked: fields.BooleanField = fields.BooleanField(default=False)
    variant: fields.ChoiceField = fields.ChoiceField(
        choices=Variant,
        default=Variant.DEFAULT,
        max_length=20
    )
    position: fields.IntegerField = fields.IntegerField(default=0)

    class Meta:
        tablename = "tasks"
        registry = models_registry


class ShoppingItem(BaseModel):
    """Shopping item model for shopping lists"""
    
    user_id = fields.ForeignKey("User", on_delete="cascade", related_name="shopping_items")
    list: fields.ForeignKey = fields.ForeignKey(
        "List",
        on_delete="cascade",
        related_name="shopping_items"
    )
    title: fields.CharField = fields.CharField(max_length=255)
    url: fields.CharField = fields.CharField(max_length=500, null=True, blank=True)
    price: fields.CharField = fields.CharField(max_length=50, null=True, blank=True)
    source: fields.CharField = fields.CharField(max_length=255, null=True, blank=True)
    checked: fields.BooleanField = fields.BooleanField(default=False)
    variant: fields.ChoiceField = fields.ChoiceField(
        choices=Variant,
        default=Variant.DEFAULT,
        max_length=20
    )
    position: fields.IntegerField = fields.IntegerField(default=0)

    class Meta:
        tablename = "shopping_items"
        registry = models_registry 