import pytest
from uuid import uuid4
from datetime import datetime

from apps.todo.models import ListType, Variant


class TestListModel:
    def test_list_type_enum(self):
        """Test ListType enum values"""
        assert ListType.TASK == "task"
        assert ListType.SHOPPING == "shopping"
    
    def test_variant_enum(self):
        """Test Variant enum values"""
        assert Variant.DEFAULT == "default"
        assert Variant.OUTLINED == "outlined"
        assert Variant.FILLED == "filled"


class TestEnums:
    def test_list_type_values(self):
        """Test that ListType has correct values"""
        assert ListType.TASK == "task"
        assert ListType.SHOPPING == "shopping"
    
    def test_variant_values(self):
        """Test that Variant has correct values"""
        assert Variant.DEFAULT == "default"
        assert Variant.OUTLINED == "outlined"
        assert Variant.FILLED == "filled" 