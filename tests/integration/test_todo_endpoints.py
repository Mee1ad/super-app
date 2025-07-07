import pytest
from uuid import uuid4
from esmerald.testclient import EsmeraldTestClient

from main import app
from apps.todo.models import List, Task, ShoppingItem
from apps.todo.schemas import ListType, Variant
from db.session import database


@pytest.fixture
def test_client():
    """Create test client"""
    return EsmeraldTestClient(app=app)


@pytest.fixture
async def sample_list():
    """Create a sample list for testing"""
    list_data = {
        "id": uuid4(),
        "type": ListType.TASK,
        "title": "Test List",
        "variant": Variant.DEFAULT
    }
    list_obj = await List.objects.create(**list_data)
    yield list_obj
    await list_obj.delete()


@pytest.fixture
async def sample_task(sample_list):
    """Create a sample task for testing"""
    task_data = {
        "id": uuid4(),
        "list_id": sample_list.id,
        "title": "Test Task",
        "description": "Test Description",
        "checked": False,
        "variant": Variant.DEFAULT,
        "position": 0
    }
    task_obj = await Task.objects.create(**task_data)
    yield task_obj
    await task_obj.delete()


@pytest.fixture
async def sample_shopping_item(sample_list):
    """Create a sample shopping item for testing"""
    item_data = {
        "id": uuid4(),
        "list_id": sample_list.id,
        "title": "Test Item",
        "url": "https://example.com",
        "price": "$10.99",
        "source": "Amazon",
        "checked": False,
        "variant": Variant.DEFAULT,
        "position": 0
    }
    item_obj = await ShoppingItem.objects.create(**item_data)
    yield item_obj
    await item_obj.delete()


class TestListEndpoints:
    """Test list-related endpoints"""
    
    def test_get_lists_success(self, test_client):
        """Test successful retrieval of lists"""
        response = test_client.get("/api/lists")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_list_success(self, test_client):
        """Test successful list creation"""
        list_data = {
            "type": "task",
            "title": "New Test List",
            "variant": "default"
        }
        response = test_client.post("/api/lists", json=list_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Test List"
        assert data["type"] == "task"
    
    def test_create_list_validation_error(self, test_client):
        """Test list creation with validation error"""
        list_data = {
            "type": "task",
            "title": "",  # Empty title should fail
            "variant": "default"
        }
        response = test_client.post("/api/lists", json=list_data)
        assert response.status_code == 422
    
    def test_create_list_missing_required_field(self, test_client):
        """Test list creation with missing required field"""
        list_data = {
            "type": "task",
            # Missing title
            "variant": "default"
        }
        response = test_client.post("/api/lists", json=list_data)
        assert response.status_code == 422
    
    def test_update_list_success(self, test_client, sample_list):
        """Test successful list update"""
        update_data = {"title": "Updated List Title"}
        response = test_client.put(f"/api/lists/{sample_list.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated List Title"
    
    def test_update_list_not_found(self, test_client):
        """Test updating non-existent list"""
        update_data = {"title": "Updated Title"}
        fake_id = uuid4()
        response = test_client.put(f"/api/lists/{fake_id}", json=update_data)
        assert response.status_code == 404
    
    def test_update_list_invalid_uuid(self, test_client):
        """Test updating list with invalid UUID"""
        update_data = {"title": "Updated Title"}
        response = test_client.put("/api/lists/invalid-uuid", json=update_data)
        assert response.status_code == 400
    
    def test_delete_list_success(self, test_client, sample_list):
        """Test successful list deletion"""
        response = test_client.delete(f"/api/lists/{sample_list.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "List deleted successfully"
    
    def test_delete_list_not_found(self, test_client):
        """Test deleting non-existent list"""
        fake_id = uuid4()
        response = test_client.delete(f"/api/lists/{fake_id}")
        assert response.status_code == 404


class TestTaskEndpoints:
    """Test task-related endpoints"""
    
    async def test_get_tasks_success(self, test_client, sample_list, sample_task):
        """Test successful retrieval of tasks"""
        response = await test_client.get(f"/api/lists/{sample_list.id}/tasks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    async def test_get_tasks_list_not_found(self, test_client):
        """Test getting tasks for non-existent list"""
        fake_id = uuid4()
        response = await test_client.get(f"/api/lists/{fake_id}/tasks")
        assert response.status_code == 404
    
    async def test_get_tasks_invalid_uuid(self, test_client):
        """Test getting tasks with invalid UUID"""
        response = await test_client.get("/api/lists/invalid-uuid/tasks")
        assert response.status_code == 400
    
    async def test_create_task_success(self, test_client, sample_list):
        """Test successful task creation"""
        task_data = {
            "title": "New Test Task",
            "description": "New task description",
            "checked": False,
            "variant": "default",
            "position": 0
        }
        response = await test_client.post(f"/api/lists/{sample_list.id}/tasks", json=task_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Test Task"
        assert data["list_id"] == str(sample_list.id)
    
    async def test_create_task_validation_error(self, test_client, sample_list):
        """Test task creation with validation error"""
        task_data = {
            "title": "",  # Empty title should fail
            "description": "Valid description"
        }
        response = await test_client.post(f"/api/lists/{sample_list.id}/tasks", json=task_data)
        assert response.status_code == 422
    
    async def test_create_task_list_not_found(self, test_client):
        """Test creating task in non-existent list"""
        task_data = {"title": "Test Task"}
        fake_id = uuid4()
        response = await test_client.post(f"/api/lists/{fake_id}/tasks", json=task_data)
        assert response.status_code == 404
    
    async def test_update_task_success(self, test_client, sample_list, sample_task):
        """Test successful task update"""
        update_data = {"title": "Updated Task Title", "checked": True}
        response = await test_client.put(
            f"/api/lists/{sample_list.id}/tasks/{sample_task.id}", 
            json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Task Title"
        assert data["checked"] is True
    
    async def test_update_task_not_found(self, test_client, sample_list):
        """Test updating non-existent task"""
        update_data = {"title": "Updated Title"}
        fake_id = uuid4()
        response = await test_client.put(
            f"/api/lists/{sample_list.id}/tasks/{fake_id}", 
            json=update_data
        )
        assert response.status_code == 404
    
    async def test_delete_task_success(self, test_client, sample_list, sample_task):
        """Test successful task deletion"""
        response = await test_client.delete(
            f"/api/lists/{sample_list.id}/tasks/{sample_task.id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Task deleted successfully"
    
    async def test_toggle_task_success(self, test_client, sample_list, sample_task):
        """Test successful task toggle"""
        response = await test_client.put(
            f"/api/lists/{sample_list.id}/tasks/{sample_task.id}/toggle"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["checked"] is True  # Should toggle from False to True
    
    async def test_reorder_tasks_success(self, test_client, sample_list):
        """Test successful task reordering"""
        # Create multiple tasks
        task1 = await Task.objects.create(
            id=uuid4(),
            list_id=sample_list.id,
            title="Task 1",
            position=0
        )
        task2 = await Task.objects.create(
            id=uuid4(),
            list_id=sample_list.id,
            title="Task 2",
            position=1
        )
        
        reorder_data = {"item_ids": [str(task2.id), str(task1.id)]}
        response = await test_client.put(
            f"/api/lists/{sample_list.id}/tasks/reorder",
            json=reorder_data
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Cleanup
        await task1.delete()
        await task2.delete()
    
    async def test_reorder_tasks_validation_error(self, test_client, sample_list):
        """Test task reordering with validation error"""
        reorder_data = {"item_ids": []}  # Empty list should fail
        response = await test_client.put(
            f"/api/lists/{sample_list.id}/tasks/reorder",
            json=reorder_data
        )
        assert response.status_code == 422


class TestShoppingItemEndpoints:
    """Test shopping item-related endpoints"""
    
    async def test_get_items_success(self, test_client, sample_list, sample_shopping_item):
        """Test successful retrieval of shopping items"""
        response = await test_client.get(f"/api/lists/{sample_list.id}/items")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    async def test_create_item_success(self, test_client, sample_list):
        """Test successful shopping item creation"""
        item_data = {
            "title": "New Test Item",
            "url": "https://example.com",
            "price": "$15.99",
            "source": "Amazon",
            "checked": False,
            "variant": "default",
            "position": 0
        }
        response = await test_client.post(f"/api/lists/{sample_list.id}/items", json=item_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Test Item"
        assert data["list_id"] == str(sample_list.id)
    
    async def test_create_item_validation_error(self, test_client, sample_list):
        """Test shopping item creation with validation error"""
        item_data = {
            "title": "",  # Empty title should fail
            "price": "$15.99"
        }
        response = await test_client.post(f"/api/lists/{sample_list.id}/items", json=item_data)
        assert response.status_code == 422
    
    async def test_update_item_success(self, test_client, sample_list, sample_shopping_item):
        """Test successful shopping item update"""
        update_data = {"title": "Updated Item Title", "price": "$20.99"}
        response = await test_client.put(
            f"/api/lists/{sample_list.id}/items/{sample_shopping_item.id}", 
            json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Item Title"
        assert data["price"] == "$20.99"
    
    async def test_delete_item_success(self, test_client, sample_list, sample_shopping_item):
        """Test successful shopping item deletion"""
        response = await test_client.delete(
            f"/api/lists/{sample_list.id}/items/{sample_shopping_item.id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Shopping item deleted successfully"
    
    async def test_toggle_item_success(self, test_client, sample_list, sample_shopping_item):
        """Test successful shopping item toggle"""
        response = await test_client.put(
            f"/api/lists/{sample_list.id}/items/{sample_shopping_item.id}/toggle"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["checked"] is True  # Should toggle from False to True
    
    async def test_reorder_items_success(self, test_client, sample_list):
        """Test successful shopping item reordering"""
        # Create multiple items
        item1 = await ShoppingItem.objects.create(
            id=uuid4(),
            list_id=sample_list.id,
            title="Item 1",
            position=0
        )
        item2 = await ShoppingItem.objects.create(
            id=uuid4(),
            list_id=sample_list.id,
            title="Item 2",
            position=1
        )
        
        reorder_data = {"item_ids": [str(item2.id), str(item1.id)]}
        response = await test_client.put(
            f"/api/lists/{sample_list.id}/items/reorder",
            json=reorder_data
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Cleanup
        await item1.delete()
        await item2.delete()


class TestSearchEndpoints:
    """Test search-related endpoints"""
    
    async def test_search_success(self, test_client, sample_list, sample_task):
        """Test successful search"""
        response = await test_client.get("/api/search?q=test")
        assert response.status_code == 200
        data = response.json()
        assert "lists" in data
        assert "tasks" in data
        assert "shopping_items" in data
    
    async def test_search_short_query(self, test_client):
        """Test search with query too short"""
        response = await test_client.get("/api/search?q=a")
        assert response.status_code == 400
    
    async def test_search_missing_query(self, test_client):
        """Test search without query parameter"""
        response = await test_client.get("/api/search")
        assert response.status_code == 400


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    async def test_health_check_success(self, test_client):
        """Test successful health check"""
        response = await test_client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "services" in data


class TestErrorResponses:
    """Test error response formats"""
    
    async def test_404_error_format(self, test_client):
        """Test 404 error response format"""
        fake_id = uuid4()
        response = await test_client.get(f"/api/lists/{fake_id}")
        assert response.status_code == 404
        # Error response should have consistent format
    
    async def test_422_error_format(self, test_client):
        """Test 422 error response format"""
        invalid_data = {"title": ""}  # Invalid data
        response = await test_client.post("/api/lists", json=invalid_data)
        assert response.status_code == 422
        # Error response should have consistent format
    
    async def test_400_error_format(self, test_client):
        """Test 400 error response format"""
        response = await test_client.get("/api/lists/invalid-uuid/tasks")
        assert response.status_code == 400
        # Error response should have consistent format 