import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, date

from apps.replicache.services import (
    process_todo_mutation, process_food_mutation,
    process_diary_mutation, process_ideas_mutation,
    get_todo_patch, get_food_patch, get_diary_patch, get_ideas_patch
)


class TestTodoMutations:
    """Test todo mutation processing"""
    
    @pytest.mark.asyncio
    async def test_process_todo_mutation_create_list(self):
        """Test creating a todo list"""
        mutation = {
            'name': 'createList',
            'args': {
                'id': 'list-123',
                'title': 'New List',
                'type': 'task',
                'variant': 'default'
            }
        }
        
        with patch('apps.replicache.services.TodoList.query.get') as mock_get_list, \
             patch('apps.replicache.services.TodoList.query.create') as mock_create_list:
            
            # Mock that list doesn't exist
            mock_get_list.side_effect = Exception("List not found")
            
            await process_todo_mutation(mutation, "test-user-id")
            
            # The convert_to_uuid function converts 'list-123' to a UUID
            # We need to check that the mock was called with the converted UUID
            mock_get_list.assert_called_once()
            mock_create_list.assert_called_once()
            
            # Check that the create call has the correct parameters (except for the converted ID)
            create_call_args = mock_create_list.call_args[1]  # Get kwargs
            assert create_call_args['user_id'] == 'test-user-id'
            assert create_call_args['title'] == 'New List'
            assert create_call_args['type'] == 'task'
            assert create_call_args['variant'] == 'default'
            # The ID will be converted to UUID, so we just check it's a string
            assert isinstance(create_call_args['id'], str)
    
    @pytest.mark.asyncio
    async def test_process_todo_mutation_create_task(self):
        """Test creating a task"""
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
        
        with patch('apps.replicache.services.TodoList.query.get') as mock_get_list, \
             patch('apps.replicache.services.Task.query.create') as mock_create_task:
            
            mock_list = AsyncMock()
            mock_list.type = 'task'
            mock_get_list.return_value = mock_list
            
            await process_todo_mutation(mutation, "test-user-id")
            
            # The convert_to_uuid function converts IDs to UUIDs
            mock_get_list.assert_called_once()
            mock_create_task.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_todo_mutation_create_task_new_format(self):
        """Test creating a task with new createTask mutation"""
        mutation = {
            'name': 'createTask',
            'args': {
                'id': 'task-789',
                'list_id': 'list-456',
                'title': 'New Task',
                'description': 'Task description',
                'checked': False,
                'position': 0,
                'variant': 'default'
            }
        }
        
        with patch('apps.replicache.services.Task.query.get') as mock_get_task, \
             patch('apps.replicache.services.Task.query.create') as mock_create_task:
            
            # Mock that task doesn't exist
            mock_get_task.side_effect = Exception("Task not found")
            
            await process_todo_mutation(mutation, "test-user-id")
            
            # The convert_to_uuid function converts IDs to UUIDs
            # We need to check that the mock was called with the converted UUIDs
            mock_get_task.assert_called_once()
            mock_create_task.assert_called_once()
            
            # Check that the create call has the correct parameters (except for the converted IDs)
            create_call_args = mock_create_task.call_args[1]  # Get kwargs
            assert create_call_args['user_id'] == 'test-user-id'
            assert create_call_args['title'] == 'New Task'
            assert create_call_args['description'] == 'Task description'
            assert create_call_args['checked'] == False
            assert create_call_args['position'] == 0
            assert create_call_args['variant'] == 'default'
            # The IDs will be converted to UUIDs, so we just check they're strings
            assert isinstance(create_call_args['id'], str)
            assert isinstance(create_call_args['list'], str)
    
    @pytest.mark.asyncio
    async def test_process_todo_mutation_create_shopping_item(self):
        """Test creating a shopping item"""
        mutation = {
            'name': 'createItem',
            'args': {
                'id': 'item-123',
                'listId': 'list-456',
                'title': 'Milk',
                'completed': False,
                'order': 0
            }
        }
        
        with patch('apps.replicache.services.TodoList.query.get') as mock_get_list, \
             patch('apps.replicache.services.ShoppingItem.query.create') as mock_create_item:
            
            mock_list = AsyncMock()
            mock_list.type = 'shopping'
            mock_get_list.return_value = mock_list
            
            await process_todo_mutation(mutation, "test-user-id")
            
            # The convert_to_uuid function converts IDs to UUIDs
            mock_get_list.assert_called_once()
            mock_create_item.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_todo_mutation_update(self):
        """Test updating a todo item"""
        mutation = {
            'name': 'updateItem',
            'args': {
                'id': 'task-123',
                'title': 'Updated Task',
                'completed': True,
                'order': 1
            }
        }
        
        with patch('apps.replicache.services.Task.query.filter') as mock_filter_task, \
             patch('apps.replicache.services.ShoppingItem.query.filter') as mock_filter_item:
            
            mock_filter_task.return_value.update = AsyncMock()
            mock_filter_item.return_value.update = AsyncMock()
            
            await process_todo_mutation(mutation, "test-user-id")
            
            # Should try task first, then shopping item
            # The convert_to_uuid function converts IDs to UUIDs
            mock_filter_task.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_todo_mutation_delete(self):
        """Test deleting a todo item"""
        mutation = {
            'name': 'deleteItem',
            'args': {
                'id': 'task-123'
            }
        }
        
        with patch('apps.replicache.services.Task.query.filter') as mock_filter_task, \
             patch('apps.replicache.services.ShoppingItem.query.filter') as mock_filter_item:
            
            mock_filter_task.return_value.delete = AsyncMock()
            mock_filter_item.return_value.delete = AsyncMock()
            
            await process_todo_mutation(mutation, "test-user-id")
            
            # The convert_to_uuid function converts IDs to UUIDs
            mock_filter_task.assert_called_once()


class TestFoodMutations:
    """Test food mutation processing"""
    
    @pytest.mark.asyncio
    async def test_process_food_mutation_create(self):
        """Test creating a food entry"""
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
        
        with patch('apps.replicache.services.FoodEntry.query.create') as mock_create:
            await process_food_mutation(mutation, "test-user-id")
            
            mock_create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_food_mutation_update(self):
        """Test updating a food entry"""
        mutation = {
            'name': 'updateEntry',
            'args': {
                'id': 'food-123',
                'name': 'Updated Pizza',
                'price': 20.99
            }
        }
        
        with patch('apps.replicache.services.FoodEntry.query.filter') as mock_filter:
            mock_filter.return_value.update = AsyncMock()
            
            await process_food_mutation(mutation, "test-user-id")
            
            # The convert_to_uuid function converts IDs to UUIDs
            mock_filter.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_food_mutation_delete(self):
        """Test deleting a food entry"""
        mutation = {
            'name': 'deleteEntry',
            'args': {
                'id': 'food-123'
            }
        }
        
        with patch('apps.replicache.services.FoodEntry.query.filter') as mock_filter:
            mock_filter.return_value.delete = AsyncMock()
            
            await process_food_mutation(mutation, "test-user-id")
            
            # The convert_to_uuid function converts IDs to UUIDs
            mock_filter.assert_called_once()


class TestDiaryMutations:
    """Test diary mutation processing"""
    
    @pytest.mark.asyncio
    async def test_process_diary_mutation_create(self):
        """Test creating a diary entry"""
        mutation = {
            'name': 'createEntry',
            'args': {
                'id': 'diary-123',
                'title': 'Today was great',
                'content': 'I had a wonderful day!',
                'date': '2024-01-15'
            }
        }
        
        with patch('apps.replicache.services.DiaryEntry.query.create') as mock_create:
            await process_diary_mutation(mutation, "test-user-id")
            
            mock_create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_diary_mutation_update(self):
        """Test updating a diary entry"""
        mutation = {
            'name': 'updateEntry',
            'args': {
                'id': 'diary-123',
                'title': 'Updated Entry',
                'content': 'Updated content'
            }
        }
        
        with patch('apps.replicache.services.DiaryEntry.query.filter') as mock_filter:
            mock_filter.return_value.update = AsyncMock()
            
            await process_diary_mutation(mutation, "test-user-id")
            
            # The convert_to_uuid function converts IDs to UUIDs
            mock_filter.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_diary_mutation_delete(self):
        """Test deleting a diary entry"""
        mutation = {
            'name': 'deleteEntry',
            'args': {
                'id': 'diary-123'
            }
        }
        
        with patch('apps.replicache.services.DiaryEntry.query.filter') as mock_filter:
            mock_filter.return_value.delete = AsyncMock()
            
            await process_diary_mutation(mutation, "test-user-id")
            
            # The convert_to_uuid function converts IDs to UUIDs
            mock_filter.assert_called_once()


class TestIdeasMutations:
    """Test ideas mutation processing"""
    
    @pytest.mark.asyncio
    async def test_process_ideas_mutation_create(self):
        """Test creating an idea"""
        mutation = {
            'name': 'createIdea',
            'args': {
                'id': 'idea-123',
                'title': 'Amazing Idea',
                'description': 'This is a great idea!',
                'tags': ['innovation', 'tech']
            }
        }
        
        with patch('apps.replicache.services.Idea.query.create') as mock_create:
            await process_ideas_mutation(mutation, "test-user-id")
            
            mock_create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_ideas_mutation_update(self):
        """Test updating an idea"""
        mutation = {
            'name': 'updateIdea',
            'args': {
                'id': 'idea-123',
                'title': 'Updated Idea',
                'description': 'Updated description'
            }
        }
        
        with patch('apps.replicache.services.Idea.query.filter') as mock_filter:
            mock_filter.return_value.update = AsyncMock()
            
            await process_ideas_mutation(mutation, "test-user-id")
            
            # The convert_to_uuid function converts IDs to UUIDs
            mock_filter.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_ideas_mutation_delete(self):
        """Test deleting an idea"""
        mutation = {
            'name': 'deleteIdea',
            'args': {
                'id': 'idea-123'
            }
        }
        
        with patch('apps.replicache.services.Idea.query.filter') as mock_filter:
            mock_filter.return_value.delete = AsyncMock()
            
            await process_ideas_mutation(mutation, "test-user-id")
            
            # The convert_to_uuid function converts IDs to UUIDs
            mock_filter.assert_called_once()


class TestPatchGeneration:
    """Test patch generation for different contexts"""
    
    @pytest.mark.asyncio
    async def test_get_todo_patch(self):
        """Test todo patch generation"""
        with patch('apps.replicache.services.TodoList.query.filter') as mock_lists, \
             patch('apps.replicache.services.Task.query.filter') as mock_tasks, \
             patch('apps.replicache.services.ShoppingItem.query.filter') as mock_items:

            # Mock list data
            mock_list = MagicMock()
            mock_list.id = 'list-123'
            mock_list.type = 'task'
            mock_list.title = 'Test List'
            mock_list.variant = 'default'
            mock_lists.return_value.all = AsyncMock(return_value=[mock_list])

            # Mock task data
            mock_task = MagicMock()
            mock_task.id = 'task-123'
            mock_task.list_id = 'list-123'
            mock_task.title = 'Test Task'
            mock_task.description = 'Test description'
            mock_task.checked = False
            mock_task.position = 0
            mock_task.variant = 'default'
            mock_tasks.return_value.all = AsyncMock(return_value=[mock_task])

            # Mock item data
            mock_item = MagicMock()
            mock_item.id = 'item-123'
            mock_item.list_id = 'list-456'
            mock_item.title = 'Test Item'
            mock_item.url = None
            mock_item.price = None
            mock_item.source = None
            mock_item.checked = False
            mock_item.position = 0
            mock_item.variant = 'default'
            mock_items.return_value.all = AsyncMock(return_value=[mock_item])

            patch_data = await get_todo_patch("test-user-id")

            assert len(patch_data) == 3  # 1 list + 1 task + 1 item
            assert patch_data[0]["key"] == "list/list-123"
            assert patch_data[1]["key"] == "task/task-123"
            assert patch_data[2]["key"] == "item/item-123"
    
    @pytest.mark.asyncio
    async def test_get_food_patch(self):
        """Test food patch generation"""
        with patch('apps.replicache.services.FoodEntry.query.filter') as mock_entries:
            mock_entry = MagicMock()
            mock_entry.id = 'food-123'
            mock_entry.name = 'Pizza'
            mock_entry.price = 15.99
            mock_entry.description = 'Delicious pizza'
            mock_entry.image_url = None
            mock_entry.date = datetime(2024, 1, 15, 12, 0, 0)
            mock_entries.return_value.all = AsyncMock(return_value=[mock_entry])
            
            patch_data = await get_food_patch("test-user-id")
            
            assert len(patch_data) == 1
            assert patch_data[0]["key"] == "food-entry/food-123"
            assert patch_data[0]["value"]["name"] == "Pizza"
    
    @pytest.mark.asyncio
    async def test_get_diary_patch(self):
        """Test diary patch generation"""
        with patch('apps.replicache.services.DiaryEntry.query.filter') as mock_entries:
            mock_entry = MagicMock()
            mock_entry.id = 'diary-123'
            mock_entry.title = 'Today was great'
            mock_entry.content = 'I had a wonderful day!'
            mock_entry.mood_id = None
            mock_entry.date = date(2024, 1, 15)
            mock_entry.created_at = datetime(2024, 1, 15, 10, 0, 0)
            mock_entry.updated_at = datetime(2024, 1, 15, 10, 0, 0)
            mock_entries.return_value.all = AsyncMock(return_value=[mock_entry])
            
            patch_data = await get_diary_patch("test-user-id")
            
            assert len(patch_data) == 1
            assert patch_data[0]["key"] == "diary-entry/diary-123"
            assert patch_data[0]["value"]["title"] == "Today was great"
    
    @pytest.mark.asyncio
    async def test_get_ideas_patch(self):
        """Test ideas patch generation"""
        with patch('apps.replicache.services.Idea.query.filter') as mock_ideas:
            mock_idea = MagicMock()
            mock_idea.id = 'idea-123'
            mock_idea.title = 'Amazing Idea'
            mock_idea.description = 'This is a great idea!'
            mock_idea.category_id = None
            mock_idea.tags = ['innovation', 'tech']
            mock_idea.is_archived = False
            mock_idea.created_at = datetime(2024, 1, 15, 10, 0, 0)
            mock_idea.updated_at = datetime(2024, 1, 15, 10, 0, 0)
            mock_ideas.return_value.all = AsyncMock(return_value=[mock_idea])
            
            patch_data = await get_ideas_patch("test-user-id")
            
            assert len(patch_data) == 1
            assert patch_data[0]["key"] == "idea/idea-123"
            assert patch_data[0]["value"]["title"] == "Amazing Idea" 