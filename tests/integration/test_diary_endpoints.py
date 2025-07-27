import pytest
from uuid import uuid4
from httpx import AsyncClient
from apps.auth.models import User
from unittest.mock import patch

# Adjust import paths as needed for your project structure
from backend.main import app

def create_auth_headers(user_id: str):
    """Create authentication headers with a mock JWT token"""
    return {"Authorization": f"Bearer mock_token_for_user_{user_id}"}

import pytest_asyncio

@pytest_asyncio.fixture
async def test_user():
    """Create a test user for integration tests"""
    user_data = {
        "id": uuid4(),
        "email": "integration@example.com",
        "username": "integrationuser",
        "hashed_password": "hashed_password_integration",
        "is_active": True
    }
    user = await User.query.create(**user_data)
    yield user
    await user.delete()

class TestDiaryEndpoints:
    """Test diary-related endpoints"""

    @pytest.mark.asyncio
    async def test_get_moods_success(self, test_client, setup_database):
        """Test getting all moods"""
        response = test_client.get("/api/v1/moods")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "moods" in data
        assert isinstance(data["moods"], list)
        # Should have seeded moods
        assert len(data["moods"]) > 0

    @pytest.mark.asyncio
    async def test_get_diary_entries_success(self, test_client, test_user, setup_database):
        """Test getting diary entries for authenticated user"""
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            response = test_client.get("/api/v1/diary-entries", headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict)
            assert "entries" in data
            assert "meta" in data
            assert isinstance(data["entries"], list)

    @pytest.mark.asyncio
    async def test_get_diary_entries_with_search(self, test_client, test_user, setup_database):
        """Test getting diary entries with search parameter"""
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            response = test_client.get("/api/v1/diary-entries?search=test", headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict)
            assert "entries" in data

    @pytest.mark.asyncio
    async def test_get_diary_entries_with_pagination(self, test_client, test_user, setup_database):
        """Test getting diary entries with pagination"""
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            response = test_client.get("/api/v1/diary-entries?page=1&limit=10", headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict)
            assert "entries" in data
            assert "meta" in data
            assert data["meta"]["page"] == 1
            assert data["meta"]["limit"] == 10

    @pytest.mark.asyncio
    async def test_create_diary_entry_success(self, test_client, test_user, setup_database):
        """Test creating a diary entry"""
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            diary_data = {
                "title": "Test Entry",
                "content": "This is a test diary entry.",
                "mood": None,
                "date": "2024-01-01",
                "images": []
            }
            response = test_client.post("/api/v1/diary-entries", json=diary_data, headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == "Test Entry"
            assert data["content"] == "This is a test diary entry."
            assert "id" in data

    @pytest.mark.asyncio
    async def test_create_diary_entry_with_mood(self, test_client, test_user, setup_database):
        """Test creating a diary entry with mood"""
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            # First create a mood in the database
            from apps.diary.models import Mood
            mood = await Mood.query.create(
                name="Happy",
                emoji="😊",
                color="#00ff00"
            )
            
            diary_data = {
                "title": "Test Entry with Mood",
                "content": "This is a test diary entry with mood.",
                "mood": str(mood.id),  # Convert UUID to string
                "date": "2024-01-01",
                "images": []
            }
            response = test_client.post("/api/v1/diary-entries", json=diary_data, headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == "Test Entry with Mood"
            assert data["mood"] == str(mood.id)

    @pytest.mark.asyncio
    async def test_create_diary_entry_validation_error(self, test_client, test_user, setup_database):
        """Test creating a diary entry with invalid data"""
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            diary_data = {
                "title": "",  # Invalid empty title
                "content": "This is a test diary entry.",
                "date": "2024-01-01",
                "images": []
            }
            response = test_client.post("/api/v1/diary-entries", json=diary_data, headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_get_diary_entry_success(self, test_client, test_user, setup_database):
        """Test getting a specific diary entry"""
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            # First create an entry
            diary_data = {
                "title": "Test Entry for Get",
                "content": "This is a test diary entry for get operation.",
                "mood": None,
                "date": "2024-01-01",
                "images": []
            }
            create_response = test_client.post("/api/v1/diary-entries", json=diary_data, headers=create_auth_headers(str(test_user.id)))
            assert create_response.status_code == 201
            entry_id = create_response.json()["id"]
            
            # Now get the entry
            response = test_client.get(f"/api/v1/diary-entries/{entry_id}", headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == entry_id
            assert data["title"] == "Test Entry for Get"

    @pytest.mark.asyncio
    async def test_get_diary_entry_not_found(self, test_client, test_user, setup_database):
        """Test getting a non-existent diary entry"""
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            fake_id = uuid4()
            response = test_client.get(f"/api/v1/diary-entries/{fake_id}", headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_diary_entry_success(self, test_client, test_user, setup_database):
        """Test updating a diary entry"""
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            # First create an entry
            diary_data = {
                "title": "Test Entry for Update",
                "content": "This is a test diary entry for update operation.",
                "mood": None,
                "date": "2024-01-01",
                "images": []
            }
            create_response = test_client.post("/api/v1/diary-entries", json=diary_data, headers=create_auth_headers(str(test_user.id)))
            assert create_response.status_code == 201
            entry_id = create_response.json()["id"]
            
            # Now update the entry
            update_data = {
                "title": "Updated Test Entry",
                "content": "This is an updated test diary entry."
            }
            response = test_client.put(f"/api/v1/diary-entries/{entry_id}", json=update_data, headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == entry_id
            assert data["title"] == "Updated Test Entry"
            assert data["content"] == "This is an updated test diary entry."

    @pytest.mark.asyncio
    async def test_update_diary_entry_not_found(self, test_client, test_user, setup_database):
        """Test updating a non-existent diary entry"""
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            fake_id = uuid4()
            update_data = {
                "title": "Updated Test Entry",
                "content": "This is an updated test diary entry."
            }
            response = test_client.put(f"/api/v1/diary-entries/{fake_id}", json=update_data, headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_diary_entry_success(self, test_client, test_user, setup_database):
        """Test deleting a diary entry"""
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            # First create an entry
            diary_data = {
                "title": "Test Entry for Delete",
                "content": "This is a test diary entry for delete operation.",
                "mood": None,
                "date": "2024-01-01",
                "images": []
            }
            create_response = test_client.post("/api/v1/diary-entries", json=diary_data, headers=create_auth_headers(str(test_user.id)))
            assert create_response.status_code == 201
            entry_id = create_response.json()["id"]
            
            # Now delete the entry
            response = test_client.delete(f"/api/v1/diary-entries/{entry_id}", headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Diary entry deleted successfully"
            
            # Verify the entry is deleted
            get_response = test_client.get(f"/api/v1/diary-entries/{entry_id}", headers=create_auth_headers(str(test_user.id)))
            assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_diary_entry_not_found(self, test_client, test_user, setup_database):
        """Test deleting a non-existent diary entry"""
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            fake_id = uuid4()
            response = test_client.delete(f"/api/v1/diary-entries/{fake_id}", headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_diary_endpoints_require_auth(self, test_client, setup_database):
        """Test that diary endpoints require authentication"""
        # Test without auth headers - should return 401
        response = test_client.get("/api/v1/diary-entries")
        assert response.status_code == 401
        
        # Use valid data so it reaches authentication check
        valid_data = {
            "title": "Test Entry",
            "content": "Test content",
            "date": "2024-01-01",
            "images": []
        }
        response = test_client.post("/api/v1/diary-entries", json=valid_data)
        assert response.status_code == 401
        
        fake_id = uuid4()
        response = test_client.get(f"/api/v1/diary-entries/{fake_id}")
        assert response.status_code == 401
        
        response = test_client.put(f"/api/v1/diary-entries/{fake_id}", json=valid_data)
        assert response.status_code == 401
        
        response = test_client.delete(f"/api/v1/diary-entries/{fake_id}")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_diary_endpoints_invalid_uuid(self, test_client, test_user, setup_database):
        """Test diary endpoints with invalid UUID format"""
        with patch('core.dependencies.get_current_user_dependency') as mock_auth:
            mock_auth.return_value = test_user
            # Test with invalid UUID format
            response = test_client.get("/api/v1/diary-entries/invalid-uuid", headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 404
            
            response = test_client.put("/api/v1/diary-entries/invalid-uuid", json={}, headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 404
            
            response = test_client.delete("/api/v1/diary-entries/invalid-uuid", headers=create_auth_headers(str(test_user.id)))
            assert response.status_code == 404 