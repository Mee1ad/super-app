import pytest
from uuid import uuid4
from datetime import datetime, timezone
from pydantic import ValidationError

from apps.todo.schemas import (
    ListCreate, ListUpdate, ListResponse,
    TaskCreate, TaskUpdate, TaskResponse,
    ShoppingItemCreate, ShoppingItemUpdate, ShoppingItemResponse,
    ReorderRequest, SearchResponse,
    ListType, Variant
)


class TestListSchemas:
    def test_list_create_valid(self):
        """Test creating a valid list"""
        data = {
            "type": ListType.TASK,
            "title": "Test List",
            "variant": Variant.DEFAULT
        }
        list_create = ListCreate(**data)
        assert list_create.title == "Test List"
        assert list_create.type == ListType.TASK
    
    def test_list_create_invalid_title(self):
        """Test creating a list with invalid title"""
        data = {
            "type": ListType.TASK,
            "title": "",  # Empty title
            "variant": Variant.DEFAULT
        }
        with pytest.raises(ValidationError):
            ListCreate(**data)
    
    def test_list_update_partial(self):
        """Test updating a list with partial data"""
        data = {"title": "Updated Title"}
        list_update = ListUpdate(**data)
        assert list_update.title == "Updated Title"
        assert list_update.variant is None
    
    def test_list_response(self):
        """Test list response schema"""
        data = {
            "id": uuid4(),
            "user_id": uuid4(),
            "type": ListType.SHOPPING,
            "title": "Shopping List",
            "variant": Variant.OUTLINED,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        list_response = ListResponse(**data)
        assert list_response.id == data["id"]
        assert list_response.title == "Shopping List"


class TestTaskSchemas:
    def test_task_create_valid(self):
        """Test creating a valid task"""
        data = {
            "title": "Test Task",
            "description": "Test Description",
            "checked": False,
            "variant": Variant.DEFAULT,
            "position": 1
        }
        task_create = TaskCreate(**data)
        assert task_create.title == "Test Task"
        assert task_create.description == "Test Description"
        assert task_create.checked is False
    
    def test_task_create_minimal(self):
        """Test creating a task with minimal data"""
        data = {"title": "Minimal Task"}
        task_create = TaskCreate(**data)
        assert task_create.title == "Minimal Task"
        assert task_create.checked is False
        assert task_create.position == 0
    
    def test_task_update_partial(self):
        """Test updating a task with partial data"""
        data = {"title": "Updated Task", "checked": True}
        task_update = TaskUpdate(**data)
        assert task_update.title == "Updated Task"
        assert task_update.checked is True
        assert task_update.description is None
    
    def test_task_response(self):
        """Test task response schema"""
        data = {
            "id": uuid4(),
            "list_id": uuid4(),
            "user_id": uuid4(),
            "title": "Test Task",
            "description": "Test Description",
            "checked": True,
            "variant": Variant.FILLED,
            "position": 2,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        task_response = TaskResponse(**data)
        assert task_response.id == data["id"]
        assert task_response.list_id == data["list_id"]
        assert task_response.checked is True


class TestShoppingItemSchemas:
    def test_shopping_item_create_valid(self):
        """Test creating a valid shopping item"""
        data = {
            "title": "Test Item",
            "url": "https://example.com",
            "price": "$10.99",
            "source": "Amazon",
            "checked": False,
            "variant": Variant.DEFAULT,
            "position": 1
        }
        item_create = ShoppingItemCreate(**data)
        assert item_create.title == "Test Item"
        assert item_create.url == "https://example.com"
        assert item_create.price == "$10.99"
    
    def test_shopping_item_create_minimal(self):
        """Test creating a shopping item with minimal data"""
        data = {"title": "Minimal Item"}
        item_create = ShoppingItemCreate(**data)
        assert item_create.title == "Minimal Item"
        assert item_create.checked is False
        assert item_create.position == 0
        assert item_create.url is None
    
    def test_shopping_item_update_partial(self):
        """Test updating a shopping item with partial data"""
        data = {"title": "Updated Item", "price": "$15.99"}
        item_update = ShoppingItemUpdate(**data)
        assert item_update.title == "Updated Item"
        assert item_update.price == "$15.99"
        assert item_update.url is None
    
    def test_shopping_item_response(self):
        """Test shopping item response schema"""
        data = {
            "id": uuid4(),
            "list_id": uuid4(),
            "user_id": uuid4(),
            "title": "Test Item",
            "url": "https://example.com",
            "price": "$10.99",
            "source": "Amazon",
            "checked": True,
            "variant": Variant.OUTLINED,
            "position": 3,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        item_response = ShoppingItemResponse(**data)
        assert item_response.id == data["id"]
        assert item_response.list_id == data["list_id"]
        assert item_response.checked is True


class TestReorderSchemas:
    def test_reorder_request_valid(self):
        """Test valid reorder request"""
        item_ids = [uuid4(), uuid4(), uuid4()]
        reorder_request = ReorderRequest(item_ids=item_ids)
        assert reorder_request.item_ids == item_ids
    
    def test_reorder_request_empty(self):
        """Test reorder request with empty list"""
        with pytest.raises(ValidationError):
            ReorderRequest(item_ids=[])


class TestSearchSchemas:
    def test_search_response(self):
        """Test search response schema"""
        list_response = ListResponse(
            id=uuid4(),
            user_id=uuid4(),
            type=ListType.TASK,
            title="Test List",
            variant=Variant.DEFAULT,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        task_response = TaskResponse(
            id=uuid4(),
            list_id=uuid4(),
            user_id=uuid4(),
            title="Test Task",
            description="Test Description",
            checked=False,
            variant=Variant.DEFAULT,
            position=0,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        item_response = ShoppingItemResponse(
            id=uuid4(),
            list_id=uuid4(),
            user_id=uuid4(),
            title="Test Item",
            url="https://example.com",
            price="$10.99",
            source="Amazon",
            checked=False,
            variant=Variant.DEFAULT,
            position=0,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        search_response = SearchResponse(
            lists=[list_response],
            tasks=[task_response],
            shopping_items=[item_response]
        )
        
        assert len(search_response.lists) == 1
        assert len(search_response.tasks) == 1
        assert len(search_response.shopping_items) == 1 