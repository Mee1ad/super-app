import pytest
import pytest_asyncio
from uuid import uuid4
from esmerald.testclient import EsmeraldTestClient
from unittest.mock import patch

from main import app
from apps.todo.models import List, Task, ShoppingItem
from apps.todo.schemas import ListType, Variant
from apps.auth.models import User
from db.session import database


def create_auth_headers(user_id: str):
    """Create authentication headers with a mock JWT token"""
    return {"Authorization": f"Bearer mock_token_for_user_{user_id}"}

@pytest_asyncio.fixture
async def test_user():
    """Create a test user for integration tests"""
    user_data = {
        "id": uuid4(),
        "email": "integration@example.com",
        "name": "Integration Test User",
        "is_active": True,
        "is_verified": True
    }
    user = await User.query.create(**user_data)
    yield user
    await user.delete()

@pytest_asyncio.fixture
async def sample_list(test_user):
    """Create a sample list for testing"""
    list_data = {
        "id": uuid4(),
        "user_id": test_user,
        "type": ListType.TASK,
        "title": "Test List",
        "variant": Variant.DEFAULT
    }
    list_obj = await List.query.create(**list_data)
    yield list_obj
    await list_obj.delete()

@pytest_asyncio.fixture
async def sample_task(test_user, sample_list):
    """Create a sample task for testing"""
    task_data = {
        "id": uuid4(),
        "user_id": test_user,
        "list": sample_list,
        "title": "Test Task",
        "description": "Test Description",
        "checked": False,
        "variant": Variant.DEFAULT,
        "position": 0
    }
    task_obj = await Task.query.create(**task_data)
    yield task_obj
    await task_obj.delete()

@pytest_asyncio.fixture
async def sample_shopping_item(test_user, sample_list):
    """Create a sample shopping item for testing"""
    item_data = {
        "id": uuid4(),
        "user_id": test_user,
        "list": sample_list,
        "title": "Test Item",
        "url": "https://example.com",
        "price": "$10.99",
        "source": "Amazon",
        "checked": False,
        "variant": Variant.DEFAULT,
        "position": 0
    }
    item_obj = await ShoppingItem.query.create(**item_data)
    yield item_obj
    await item_obj.delete()

class TestListEndpoints:
    """Test list-related endpoints"""

    @pytest.mark.asyncio
    async def test_get_lists_success(self, test_client, test_user, sample_list):
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            response = test_client.get("/api/lists", headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]["title"] == "Test List"

    @pytest.mark.asyncio
    async def test_create_list_success(self, test_client, test_user):
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            list_data = {
                "type": "task",
                "title": "New Test List",
                "variant": "default"
            }
            response = test_client.post("/api/lists", json=list_data, headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == "New Test List"
            assert data["type"] == "task"

    @pytest.mark.asyncio
    async def test_create_list_validation_error(self, test_client, test_user):
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            list_data = {
                "type": "invalid_type",
                "title": "Test List"
            }
            response = test_client.post("/api/lists", json=list_data, headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_create_list_missing_required_field(self, test_client, test_user):
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            list_data = {
                "type": "task"
            }
            response = test_client.post("/api/lists", json=list_data, headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_update_list_success(self, test_client, test_user, sample_list):
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            update_data = {"title": "Updated List Title"}
            response = test_client.put(f"/api/lists/{sample_list.id}", json=update_data, headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "Updated List Title"

    @pytest.mark.asyncio
    async def test_update_list_not_found(self, test_client, test_user):
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            update_data = {"title": "Updated Title"}
            fake_id = uuid4()
            response = test_client.put(f"/api/lists/{fake_id}", json=update_data, headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 404

    def test_update_list_invalid_uuid(self, test_client):
        update_data = {"title": "Updated Title"}
        response = test_client.put("/api/lists/invalid-uuid", json=update_data)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_list_success(self, test_client, test_user, sample_list):
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            response = test_client.delete(f"/api/lists/{sample_list.id}", headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "List deleted successfully"

    @pytest.mark.asyncio
    async def test_delete_list_not_found(self, test_client, test_user):
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            fake_id = uuid4()
            response = test_client.delete(f"/api/lists/{fake_id}", headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 404

class TestTaskEndpoints:
    """Test task-related endpoints"""

    @pytest.mark.asyncio
    async def test_get_tasks_success(self, test_client, test_user, sample_list, sample_task):
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            response = test_client.get(f"/api/lists/{sample_list.id}/tasks", headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_get_tasks_list_not_found(self, test_client, test_user):
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            fake_id = uuid4()
            response = test_client.get(f"/api/lists/{fake_id}/tasks", headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 404

    def test_get_tasks_invalid_uuid(self, test_client):
        response = test_client.get("/api/lists/invalid-uuid/tasks")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_task_success(self, test_client, test_user, sample_list):
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            task_data = {
                "title": "New Test Task",
                "description": "New task description",
                "checked": False,
                "variant": "default",
                "position": 0
            }
            response = test_client.post(f"/api/lists/{sample_list.id}/tasks", json=task_data, headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == "New Test Task"
            assert data["list_id"] == str(sample_list.id)

    @pytest.mark.asyncio
    async def test_create_task_validation_error(self, test_client, test_user, sample_list):
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            task_data = {
                "title": "",
                "description": "Test Description"
            }
            response = test_client.post(f"/api/lists/{sample_list.id}/tasks", json=task_data, headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_create_task_list_not_found(self, test_client, test_user):
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            task_data = {"title": "Test Task"}
            fake_id = uuid4()
            response = test_client.post(f"/api/lists/{fake_id}/tasks", json=task_data, headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_task_success(self, test_client, test_user, sample_list, sample_task):
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            update_data = {"title": "Updated Task Title", "checked": True}
            response = test_client.put(f"/api/lists/{sample_list.id}/tasks/{sample_task.id}", json=update_data, headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "Updated Task Title"
            assert data["checked"] is True

    @pytest.mark.asyncio
    async def test_update_task_not_found(self, test_client, test_user):
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            update_data = {"title": "Updated Title"}
            fake_id = uuid4()
            response = test_client.put(f"/api/lists/{fake_id}/tasks/{fake_id}", json=update_data, headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_task_success(self, test_client, test_user, sample_list, sample_task):
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            response = test_client.delete(f"/api/lists/{sample_list.id}/tasks/{sample_task.id}", headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Task deleted successfully"

    @pytest.mark.asyncio
    async def test_toggle_task_success(self, test_client, test_user, sample_list, sample_task):
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            response = test_client.put(f"/api/lists/{sample_list.id}/tasks/{sample_task.id}/toggle", headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 200
            data = response.json()
            assert data["checked"] != sample_task.checked  # Should be toggled

    @pytest.mark.asyncio
    async def test_reorder_tasks_success(self, test_client, test_user, sample_list):
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            task1 = await Task.query.create(
                id=uuid4(),
                user_id=test_user,
                list=sample_list,
                title="Task 1",
                position=0
            )
            task2 = await Task.query.create(
                id=uuid4(),
                user_id=test_user,
                list=sample_list,
                title="Task 2",
                position=1
            )
            reorder_data = {
                "item_ids": [str(task2.id), str(task1.id)]
            }
            response = test_client.put(f"/api/lists/{sample_list.id}/tasks/reorder", json=reorder_data, headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 200
            await task1.delete()
            await task2.delete()

    @pytest.mark.asyncio
    async def test_reorder_tasks_validation_error(self, test_client, test_user, sample_list):
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            reorder_data = {
                "item_ids": []
            }
            response = test_client.put(f"/api/lists/{sample_list.id}/tasks/reorder", json=reorder_data, headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 400

class TestShoppingItemEndpoints:
    """Test shopping item-related endpoints"""

    @pytest.mark.asyncio
    async def test_get_items_success(self, test_client, test_user, sample_list, sample_shopping_item):
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            response = test_client.get(f"/api/lists/{sample_list.id}/items", headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_create_item_success(self, test_client, test_user, sample_list):
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            item_data = {
                "title": "New Test Item",
                "url": "https://example.com/new",
                "price": "$15.99",
                "source": "Amazon",
                "checked": False,
                "variant": "default",
                "position": 0
            }
            response = test_client.post(f"/api/lists/{sample_list.id}/items", json=item_data, headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == "New Test Item"
            assert data["list_id"] == str(sample_list.id)

    @pytest.mark.asyncio
    async def test_create_item_validation_error(self, test_client, test_user, sample_list):
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            item_data = {
                "title": "",
                "url": "https://example.com"
            }
            response = test_client.post(f"/api/lists/{sample_list.id}/items", json=item_data, headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_update_item_success(self, test_client, test_user, sample_list, sample_shopping_item):
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            update_data = {"title": "Updated Item Title", "checked": True}
            response = test_client.put(f"/api/lists/{sample_list.id}/items/{sample_shopping_item.id}", json=update_data, headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "Updated Item Title"
            assert data["checked"] is True

    @pytest.mark.asyncio
    async def test_delete_item_success(self, test_client, test_user, sample_list, sample_shopping_item):
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            response = test_client.delete(f"/api/lists/{sample_list.id}/items/{sample_shopping_item.id}", headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Shopping item deleted successfully"

    @pytest.mark.asyncio
    async def test_toggle_item_success(self, test_client, test_user, sample_list, sample_shopping_item):
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            response = test_client.put(f"/api/lists/{sample_list.id}/items/{sample_shopping_item.id}/toggle", headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 200
            data = response.json()
            assert data["checked"] != sample_shopping_item.checked  # Should be toggled

    @pytest.mark.asyncio
    async def test_reorder_items_success(self, test_client, test_user, sample_list):
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            item1 = await ShoppingItem.query.create(
                id=uuid4(),
                user_id=test_user,
                list=sample_list,
                title="Item 1",
                position=0
            )
            item2 = await ShoppingItem.query.create(
                id=uuid4(),
                user_id=test_user,
                list=sample_list,
                title="Item 2",
                position=1
            )
            reorder_data = {
                "item_ids": [str(item2.id), str(item1.id)]
            }
            response = test_client.put(f"/api/lists/{sample_list.id}/items/reorder", json=reorder_data, headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 200
            await item1.delete()
            await item2.delete()

class TestSearchEndpoints:
    """Test search-related endpoints"""

    @pytest.mark.asyncio
    async def test_search_success(self, test_client, test_user, sample_list, sample_task):
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            response = test_client.get("/api/search?q=Test", headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict)
            assert "lists" in data
            assert "tasks" in data
            assert "shopping_items" in data

    def test_search_short_query(self, test_client):
        response = test_client.get("/api/search?q=ab")
        assert response.status_code == 400

    def test_search_missing_query(self, test_client):
        response = test_client.get("/api/search")
        assert response.status_code == 400

class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_health_check_success(self, test_client):
        response = test_client.get("/ping")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "pong"

class TestErrorResponses:
    """Test error response formats"""

    def test_404_error_format(self, test_client):
        response = test_client.get("/api/nonexistent")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_422_error_format(self, test_client):
        response = test_client.post("/api/lists", json={})
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_400_error_format(self, test_client):
        response = test_client.put("/api/lists/invalid-uuid", json={"title": "test"})
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data 