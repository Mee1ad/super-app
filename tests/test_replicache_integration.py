import pytest
import json
from typing import Dict, Any
from unittest.mock import AsyncMock, patch

from apps.replicache.endpoints import replicache_pull, replicache_push
from apps.replicache.services import (
    process_todo_mutation, process_food_mutation,
    process_diary_mutation, process_ideas_mutation,
    get_todo_patch, get_food_patch, get_diary_patch, get_ideas_patch
)


class TestReplicachePull:
    """Test Replicache pull endpoint with different client names"""
    
    @pytest.mark.asyncio
    async def test_todo_client_pull(self):
        """Test pull endpoint for todo-replicache-flat client"""
        # Mock request
        request = AsyncMock()
        request.json.return_value = {
            'clientView': {'name': 'todo-replicache-flat'},
            'lastPulledVersion': 0
        }
        
        # Mock user dependency
        user = AsyncMock()
        user.id = "test-user-id"
        
        with patch('apps.replicache.endpoints.get_current_user_dependency', return_value=user), \
             patch('apps.replicache.services.get_todo_patch') as mock_get_todo:
            
            mock_get_todo.return_value = [
                {"op": "put", "key": "list/123", "value": {"id": "123", "title": "Test List"}}
            ]
            
            result = await replicache_pull(request)
            
            assert result["lastMutationID"] == 0
            assert result["cookie"] is None
            assert len(result["patch"]) == 1
            assert result["patch"][0]["key"] == "list/123"
            mock_get_todo.assert_called_once_with("test-user-id")
    
    @pytest.mark.asyncio
    async def test_food_client_pull(self):
        """Test pull endpoint for food-tracker-replicache client"""
        request = AsyncMock()
        request.json.return_value = {
            'clientView': {'name': 'food-tracker-replicache'},
            'lastPulledVersion': 0
        }
        
        user = AsyncMock()
        user.id = "test-user-id"
        
        with patch('apps.replicache.endpoints.get_current_user_dependency', return_value=user), \
             patch('apps.replicache.services.get_food_patch') as mock_get_food:
            
            mock_get_food.return_value = [
                {"op": "put", "key": "food-entry/456", "value": {"id": "456", "name": "Pizza"}}
            ]
            
            result = await replicache_pull(request)
            
            assert result["lastMutationID"] == 0
            assert result["cookie"] is None
            assert len(result["patch"]) == 1
            assert result["patch"][0]["key"] == "food-entry/456"
            mock_get_food.assert_called_once_with("test-user-id")
    
    @pytest.mark.asyncio
    async def test_diary_client_pull(self):
        """Test pull endpoint for diary-replicache client"""
        request = AsyncMock()
        request.json.return_value = {
            'clientView': {'name': 'diary-replicache'},
            'lastPulledVersion': 0
        }
        
        user = AsyncMock()
        user.id = "test-user-id"
        
        with patch('apps.replicache.endpoints.get_current_user_dependency', return_value=user), \
             patch('apps.replicache.services.get_diary_patch') as mock_get_diary:
            
            mock_get_diary.return_value = [
                {"op": "put", "key": "diary-entry/789", "value": {"id": "789", "title": "Today's Entry"}}
            ]
            
            result = await replicache_pull(request)
            
            assert result["lastMutationID"] == 0
            assert result["cookie"] is None
            assert len(result["patch"]) == 1
            assert result["patch"][0]["key"] == "diary-entry/789"
            mock_get_diary.assert_called_once_with("test-user-id")
    
    @pytest.mark.asyncio
    async def test_ideas_client_pull(self):
        """Test pull endpoint for ideas-replicache client"""
        request = AsyncMock()
        request.json.return_value = {
            'clientView': {'name': 'ideas-replicache'},
            'lastPulledVersion': 0
        }
        
        user = AsyncMock()
        user.id = "test-user-id"
        
        with patch('apps.replicache.endpoints.get_current_user_dependency', return_value=user), \
             patch('apps.replicache.services.get_ideas_patch') as mock_get_ideas:
            
            mock_get_ideas.return_value = [
                {"op": "put", "key": "idea/101", "value": {"id": "101", "title": "Great Idea"}}
            ]
            
            result = await replicache_pull(request)
            
            assert result["lastMutationID"] == 0
            assert result["cookie"] is None
            assert len(result["patch"]) == 1
            assert result["patch"][0]["key"] == "idea/101"
            mock_get_ideas.assert_called_once_with("test-user-id")
    
    @pytest.mark.asyncio
    async def test_unknown_client_pull(self):
        """Test pull endpoint with unknown client name"""
        request = AsyncMock()
        request.json.return_value = {
            'clientView': {'name': 'unknown-client'},
            'lastPulledVersion': 0
        }
        
        user = AsyncMock()
        user.id = "test-user-id"
        
        with patch('apps.replicache.endpoints.get_current_user_dependency', return_value=user):
            result = await replicache_pull(request)
            
            assert result["lastMutationID"] == 0
            assert result["cookie"] is None
            assert len(result["patch"]) == 0


class TestReplicachePush:
    """Test Replicache push endpoint with different client names"""
    
    @pytest.mark.asyncio
    async def test_todo_client_push(self):
        """Test push endpoint for todo-replicache-flat client"""
        request = AsyncMock()
        request.json.return_value = {
            'clientView': {'name': 'todo-replicache-flat'},
            'mutations': [
                {
                    'name': 'createItem',
                    'args': {
                        'id': 'new-task-123',
                        'listId': 'list-456',
                        'title': 'New Task',
                        'completed': False,
                        'order': 0
                    }
                }
            ]
        }
        
        user = AsyncMock()
        user.id = "test-user-id"
        
        with patch('apps.replicache.endpoints.get_current_user_dependency', return_value=user), \
             patch('apps.replicache.services.process_todo_mutation') as mock_process_todo, \
             patch('apps.replicache.endpoints.sse_manager') as mock_sse:
            
            mock_sse.user_versions = {"test-user-id": 5}
            mock_sse.notify_user = AsyncMock()
            
            result = await replicache_push(request)
            
            assert result["lastMutationID"] == 1
            assert result["cookie"] is None
            mock_process_todo.assert_called_once()
            mock_sse.notify_user.assert_called_once_with("test-user-id", "sync")
    
    @pytest.mark.asyncio
    async def test_food_client_push(self):
        """Test push endpoint for food-tracker-replicache client"""
        request = AsyncMock()
        request.json.return_value = {
            'clientView': {'name': 'food-tracker-replicache'},
            'mutations': [
                {
                    'name': 'createEntry',
                    'args': {
                        'id': 'new-food-123',
                        'name': 'Pizza',
                        'price': 15.99,
                        'description': 'Delicious pizza',
                        'date': '2024-01-15T12:00:00'
                    }
                }
            ]
        }
        
        user = AsyncMock()
        user.id = "test-user-id"
        
        with patch('apps.replicache.endpoints.get_current_user_dependency', return_value=user), \
             patch('apps.replicache.services.process_food_mutation') as mock_process_food, \
             patch('apps.replicache.endpoints.sse_manager') as mock_sse:
            
            mock_sse.user_versions = {"test-user-id": 5}
            mock_sse.notify_user = AsyncMock()
            
            result = await replicache_push(request)
            
            assert result["lastMutationID"] == 1
            assert result["cookie"] is None
            mock_process_food.assert_called_once()
            mock_sse.notify_user.assert_called_once_with("test-user-id", "sync")
    
    @pytest.mark.asyncio
    async def test_diary_client_push(self):
        """Test push endpoint for diary-replicache client"""
        request = AsyncMock()
        request.json.return_value = {
            'clientView': {'name': 'diary-replicache'},
            'mutations': [
                {
                    'name': 'createEntry',
                    'args': {
                        'id': 'new-diary-123',
                        'title': 'Today was great',
                        'content': 'I had a wonderful day!',
                        'date': '2024-01-15'
                    }
                }
            ]
        }
        
        user = AsyncMock()
        user.id = "test-user-id"
        
        with patch('apps.replicache.endpoints.get_current_user_dependency', return_value=user), \
             patch('apps.replicache.services.process_diary_mutation') as mock_process_diary, \
             patch('apps.replicache.endpoints.sse_manager') as mock_sse:
            
            mock_sse.user_versions = {"test-user-id": 5}
            mock_sse.notify_user = AsyncMock()
            
            result = await replicache_push(request)
            
            assert result["lastMutationID"] == 1
            assert result["cookie"] is None
            mock_process_diary.assert_called_once()
            mock_sse.notify_user.assert_called_once_with("test-user-id", "sync")
    
    @pytest.mark.asyncio
    async def test_ideas_client_push(self):
        """Test push endpoint for ideas-replicache client"""
        request = AsyncMock()
        request.json.return_value = {
            'clientView': {'name': 'ideas-replicache'},
            'mutations': [
                {
                    'name': 'createIdea',
                    'args': {
                        'id': 'new-idea-123',
                        'title': 'Amazing Idea',
                        'description': 'This is a great idea!',
                        'tags': ['innovation', 'tech']
                    }
                }
            ]
        }
        
        user = AsyncMock()
        user.id = "test-user-id"
        
        with patch('apps.replicache.endpoints.get_current_user_dependency', return_value=user), \
             patch('apps.replicache.services.process_ideas_mutation') as mock_process_ideas, \
             patch('apps.replicache.endpoints.sse_manager') as mock_sse:
            
            mock_sse.user_versions = {"test-user-id": 5}
            mock_sse.notify_user = AsyncMock()
            
            result = await replicache_push(request)
            
            assert result["lastMutationID"] == 1
            assert result["cookie"] is None
            mock_process_ideas.assert_called_once()
            mock_sse.notify_user.assert_called_once_with("test-user-id", "sync")
    
    @pytest.mark.asyncio
    async def test_unknown_client_push(self):
        """Test push endpoint with unknown client name"""
        request = AsyncMock()
        request.json.return_value = {
            'clientView': {'name': 'unknown-client'},
            'mutations': [
                {
                    'name': 'createSomething',
                    'args': {'id': '123'}
                }
            ]
        }
        
        user = AsyncMock()
        user.id = "test-user-id"
        
        with patch('apps.replicache.endpoints.get_current_user_dependency', return_value=user), \
             patch('apps.replicache.endpoints.sse_manager') as mock_sse:
            
            mock_sse.user_versions = {"test-user-id": 5}
            mock_sse.notify_user = AsyncMock()
            
            result = await replicache_push(request)
            
            assert result["lastMutationID"] == 1
            assert result["cookie"] is None
            mock_sse.notify_user.assert_called_once_with("test-user-id", "sync")


class TestMutationServices:
    """Test individual mutation processing services"""
    
    @pytest.mark.asyncio
    async def test_process_todo_mutation_create(self):
        """Test todo mutation processing for createItem"""
        mutation = {
            'name': 'createItem',
            'args': {
                'id': 'task-123',
                'listId': 'list-456',
                'title': 'New Task',
                'completed': False,
                'order': 0
            }
        }
        
        with patch('apps.replicache.services.List.objects.get') as mock_get_list, \
             patch('apps.replicache.services.Task.objects.create') as mock_create_task:
            
            mock_list = AsyncMock()
            mock_list.type = 'task'
            mock_get_list.return_value = mock_list
            
            await process_todo_mutation(mutation, "test-user-id")
            
            mock_get_list.assert_called_once_with(id='list-456', user_id='test-user-id')
            mock_create_task.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_food_mutation_create(self):
        """Test food mutation processing for createEntry"""
        mutation = {
            'name': 'createEntry',
            'args': {
                'id': 'food-123',
                'name': 'Pizza',
                'price': 15.99,
                'description': 'Delicious pizza',
                'date': '2024-01-15T12:00:00'
            }
        }
        
        with patch('apps.replicache.services.FoodEntry.objects.create') as mock_create:
            await process_food_mutation(mutation, "test-user-id")
            
            mock_create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_diary_mutation_create(self):
        """Test diary mutation processing for createEntry"""
        mutation = {
            'name': 'createEntry',
            'args': {
                'id': 'diary-123',
                'title': 'Today was great',
                'content': 'I had a wonderful day!',
                'date': '2024-01-15'
            }
        }
        
        with patch('apps.replicache.services.DiaryEntry.objects.create') as mock_create:
            await process_diary_mutation(mutation, "test-user-id")
            
            mock_create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_ideas_mutation_create(self):
        """Test ideas mutation processing for createIdea"""
        mutation = {
            'name': 'createIdea',
            'args': {
                'id': 'idea-123',
                'title': 'Amazing Idea',
                'description': 'This is a great idea!',
                'tags': ['innovation', 'tech']
            }
        }
        
        with patch('apps.replicache.services.Idea.objects.create') as mock_create:
            await process_ideas_mutation(mutation, "test-user-id")
            
            mock_create.assert_called_once() 