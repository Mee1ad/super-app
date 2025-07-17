import pytest
import pytest_asyncio
from uuid import uuid4
from esmerald.testclient import EsmeraldTestClient
from unittest.mock import AsyncMock, patch

from main import app
from apps.todo.models import List, Task, ShoppingItem
from apps.todo.schemas import ListType, Variant
from apps.auth.models import User
from db.session import database


@pytest_asyncio.fixture
async def test_user(setup_database):
    """Create a test user for authentication"""
    user_data = {
        "id": uuid4(),
        "email": "test@example.com",
        "username": "testuser",
        "hashed_password": "hashed_password_123",
        "is_active": True
    }
    user = await User.query.create(**user_data)
    yield user
    await user.delete()


@pytest_asyncio.fixture
async def another_user(setup_database):
    """Create another test user for isolation testing"""
    user_data = {
        "id": uuid4(),
        "email": "another@example.com",
        "username": "anotheruser",
        "hashed_password": "hashed_password_456",
        "is_active": True
    }
    user = await User.query.create(**user_data)
    yield user
    await user.delete()


@pytest_asyncio.fixture
async def sample_list(test_user):
    """Create a sample list for the test user"""
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
    """Create a sample task for the test user"""
    task_data = {
        "id": uuid4(),
        "user_id": test_user,
        "list": sample_list,
        "title": "Test Task",
        "description": "Test description",
        "checked": False,
        "variant": Variant.DEFAULT,
        "position": 0
    }
    task = await Task.query.create(**task_data)
    yield task
    await task.delete()


@pytest_asyncio.fixture
async def sample_shopping_item(test_user, sample_list):
    """Create a sample shopping item for the test user"""
    item_data = {
        "id": uuid4(),
        "user_id": test_user,
        "list": sample_list,
        "title": "Test Item",
        "url": "https://example.com",
        "price": "10.99",
        "source": "Test Store",
        "checked": False,
        "variant": Variant.DEFAULT,
        "position": 0
    }
    item = await ShoppingItem.query.create(**item_data)
    yield item
    await item.delete()


def create_auth_headers(user_id: str):
    """Create authentication headers with a mock JWT token"""
    return {"Authorization": f"Bearer mock_token_for_user_{user_id}"}


class TestTodoWithAuthentication:
    """Test todo endpoints with authentication"""

    @pytest.mark.asyncio
    async def test_get_lists_requires_auth(self, test_client: EsmeraldTestClient):
        """Test that getting lists requires authentication"""
        response = test_client.get("/api/v1/lists")
        assert response.status_code == 401

    @pytest.mark.skip(reason="Database setup required - temporarily disabled")
    @pytest.mark.asyncio
    async def test_get_lists_with_auth(self, test_client: EsmeraldTestClient, test_user, sample_list):
        """Test getting lists for authenticated user"""
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            
            response = test_client.get("/api/v1/lists", headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 200
            
            data = response.json()
            assert len(data) == 1
            assert data[0]["title"] == "Test List"
            assert data[0]["user_id"] == str(test_user.id)

    @pytest.mark.skip(reason="Database setup required - temporarily disabled")
    @pytest.mark.asyncio
    async def test_create_list_with_auth(self, test_client: EsmeraldTestClient, test_user):
        """Test creating a list for authenticated user"""
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            
            list_data = {
                "type": "task",
                "title": "New List",
                "variant": "default"
            }
            
            response = test_client.post("/api/v1/lists", json=list_data, headers=create_auth_headers(str(test_user.id)))
            assert response.status_code in (200, 201)
            
            data = response.json()
            assert data["title"] == "New List"
            assert data["user_id"] == str(test_user.id)

    @pytest.mark.skip(reason="Database setup required - temporarily disabled")
    @pytest.mark.asyncio
    async def test_update_list_with_auth(self, test_client: EsmeraldTestClient, test_user, sample_list):
        """Test updating a list for authenticated user"""
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            
            update_data = {"title": "Updated List"}
            
            response = test_client.put(f"/api/v1/lists/{sample_list.id}", json=update_data, headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 200
            
            data = response.json()
            assert data["title"] == "Updated List"

    @pytest.mark.skip(reason="Database setup required - temporarily disabled")
    @pytest.mark.asyncio
    async def test_delete_list_with_auth(self, test_client: EsmeraldTestClient, test_user, sample_list):
        """Test deleting a list for authenticated user"""
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            
            response = test_client.delete(f"/api/v1/lists/{sample_list.id}", headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 200
            
            # Verify list is deleted
            response = test_client.get("/api/v1/lists", headers=create_auth_headers(str(test_user.id)))
            data = response.json()
            assert len(data) == 0

    @pytest.mark.skip(reason="Database setup required - temporarily disabled")
    @pytest.mark.asyncio
    async def test_user_cannot_access_other_user_lists(self, test_client: EsmeraldTestClient, test_user, another_user, sample_list):
        """Test that users cannot access lists belonging to other users"""
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = another_user
            
            response = test_client.get(f"/api/v1/lists/{sample_list.id}/tasks", headers=create_auth_headers(str(another_user.id)))
            assert response.status_code == 404

    @pytest.mark.skip(reason="Database setup required - temporarily disabled")
    @pytest.mark.asyncio
    async def test_get_tasks_with_auth(self, test_client: EsmeraldTestClient, test_user, sample_list, sample_task):
        """Test getting tasks for authenticated user"""
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            
            response = test_client.get(f"/api/v1/lists/{sample_list.id}/tasks", headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 200
            
            data = response.json()
            assert len(data) == 1
            assert data[0]["title"] == "Test Task"
            assert data[0]["user_id"] == str(test_user.id)

    @pytest.mark.skip(reason="Database setup required - temporarily disabled")
    @pytest.mark.asyncio
    async def test_create_task_with_auth(self, test_client: EsmeraldTestClient, test_user, sample_list):
        """Test creating a task for authenticated user"""
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            
            task_data = {
                "title": "New Task",
                "description": "New description",
                "checked": False,
                "variant": "default",
                "position": 0
            }
            
            response = test_client.post(f"/api/v1/lists/{sample_list.id}/tasks", json=task_data, headers=create_auth_headers(str(test_user.id)))
            assert response.status_code in (200, 201)
            
            data = response.json()
            assert data["title"] == "New Task"
            assert data["user_id"] == str(test_user.id)

    @pytest.mark.skip(reason="Database setup required - temporarily disabled")
    @pytest.mark.asyncio
    async def test_get_shopping_items_with_auth(self, test_client: EsmeraldTestClient, test_user, sample_list, sample_shopping_item):
        """Test getting shopping items for authenticated user"""
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            
            response = test_client.get(f"/api/v1/lists/{sample_list.id}/items", headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 200
            
            data = response.json()
            assert len(data) == 1
            assert data[0]["title"] == "Test Item"
            assert data[0]["user_id"] == str(test_user.id)

    @pytest.mark.skip(reason="Database setup required - temporarily disabled")
    @pytest.mark.asyncio
    async def test_create_shopping_item_with_auth(self, test_client: EsmeraldTestClient, test_user, sample_list):
        """Test creating a shopping item for authenticated user"""
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            
            item_data = {
                "title": "New Item",
                "url": "https://example.com/new",
                "price": "15.99",
                "source": "New Store",
                "checked": False,
                "variant": "default",
                "position": 0
            }
            
            response = test_client.post(f"/api/v1/lists/{sample_list.id}/items", json=item_data, headers=create_auth_headers(str(test_user.id)))
            assert response.status_code in (200, 201)
            
            data = response.json()
            assert data["title"] == "New Item"
            assert data["user_id"] == str(test_user.id)

    @pytest.mark.skip(reason="Database setup required - temporarily disabled")
    @pytest.mark.asyncio
    async def test_search_with_auth(self, test_client: EsmeraldTestClient, test_user, sample_list, sample_task):
        """Test search functionality for authenticated user"""
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            
            response = test_client.get("/api/v1/search?q=Test", headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 200
            
            data = response.json()
            # Search should return results containing "Test"
            assert "lists" in data or "tasks" in data or "items" in data

    @pytest.mark.skip(reason="Database setup required - temporarily disabled")
    @pytest.mark.asyncio
    async def test_user_isolation(self, test_client: EsmeraldTestClient, test_user, another_user):
        """Test that users are properly isolated and cannot access each other's data"""
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            
            # Create a list for test_user
            list_data = {
                "type": "task",
                "title": "Test User List",
                "variant": "default"
            }
            
            response = test_client.post("/api/v1/lists", json=list_data, headers=create_auth_headers(str(test_user.id)))
            assert response.status_code in (200, 201)
            test_user_list = response.json()
            
            # Switch to another_user
            mock_auth.return_value = another_user
            
            # another_user should not see test_user's list
            response = test_client.get("/api/v1/lists", headers=create_auth_headers(str(another_user.id)))
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 0  # Should be empty for another_user 