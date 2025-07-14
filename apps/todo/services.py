# services for todo app 
from typing import List as ListType, Optional
from uuid import UUID

from edgy import Database
from edgy.exceptions import ObjectNotFound

from .models import List, Task, ShoppingItem
from .schemas import (
    ListCreate, ListUpdate, TaskCreate, TaskUpdate,
    ShoppingItemCreate, ShoppingItemUpdate, ReorderRequest
)


class ListService:
    """Service for list operations"""
    
    def __init__(self, database: Database):
        self.database = database
    
    async def get_all_lists(self, user_id: UUID) -> ListType[List]:
        """Get all lists for a specific user ordered by creation date"""
        return await List.query.filter(user_id=user_id).all().order_by("-created_at")
    
    async def get_list_by_id(self, list_id: UUID, user_id: UUID) -> List:
        """Get a list by ID for a specific user"""
        list_obj = await List.query.filter(id=list_id, user_id=user_id).first()
        if not list_obj:
            raise ObjectNotFound("List not found")
        return list_obj
    
    async def create_list(self, list_data: ListCreate, user_id: UUID) -> List:
        """Create a new list for a specific user"""
        data = list_data.model_dump()
        data['user_id'] = user_id
        return await List.query.create(**data)
    
    async def update_list(self, list_id: UUID, list_data: ListUpdate, user_id: UUID) -> List:
        """Update a list for a specific user"""
        list_obj = await self.get_list_by_id(list_id, user_id)
        update_data = {k: v for k, v in list_data.model_dump().items() if v is not None}
        await list_obj.update(**update_data)
        # Reload the list to ensure user relation is loaded
        return await self.get_list_by_id(list_id, user_id)
    
    async def delete_list(self, list_id: UUID, user_id: UUID) -> bool:
        """Delete a list and all its items for a specific user"""
        list_obj = await self.get_list_by_id(list_id, user_id)
        await list_obj.delete()
        return True


class TaskService:
    """Service for task operations"""
    
    def __init__(self, database: Database):
        self.database = database
    
    async def get_tasks_by_list(self, list_id: UUID, user_id: UUID) -> ListType[Task]:
        """Get all tasks for a specific list and user"""
        return await Task.query.filter(list=list_id, user_id=user_id).all().order_by("position")
    
    async def get_task_by_id(self, task_id: UUID, user_id: UUID) -> Task:
        """Get a task by ID for a specific user"""
        task = await Task.query.filter(id=task_id, user_id=user_id).first()
        if not task:
            raise ObjectNotFound("Task not found")
        return task
    
    async def create_task(self, task_data: dict, user_id: UUID, list_id: UUID) -> Task:
        data = dict(task_data)
        data['user_id'] = user_id
        data['list'] = list_id
        return await Task.query.create(**data)
    
    async def update_task(self, task_id: UUID, task_data: TaskUpdate, user_id: UUID) -> Task:
        """Update a task for a specific user"""
        task = await self.get_task_by_id(task_id, user_id)
        update_data = {k: v for k, v in task_data.model_dump().items() if v is not None}
        await task.update(**update_data)
        # Reload the task to ensure user relation is loaded
        return await self.get_task_by_id(task_id, user_id)
    
    async def delete_task(self, task_id: UUID, user_id: UUID) -> bool:
        """Delete a task for a specific user"""
        task = await self.get_task_by_id(task_id, user_id)
        await task.delete()
        return True
    
    async def toggle_task(self, task_id: UUID, user_id: UUID) -> Task:
        """Toggle task completion status for a specific user"""
        task = await self.get_task_by_id(task_id, user_id)
        task.checked = not task.checked
        await task.save()
        # Reload the task to ensure user relation is loaded
        return await self.get_task_by_id(task_id, user_id)
    
    async def reorder_tasks(self, list_id: UUID, reorder_data: ReorderRequest, user_id: UUID) -> None:
        """Reorder tasks for a list by updating their positions."""
        task_ids = reorder_data.item_ids
        tasks = await Task.query.filter(list=list_id, user_id=user_id).all()
        task_map = {str(task.id): task for task in tasks}
        for position, task_id in enumerate(task_ids):
            task = task_map.get(str(task_id))
            if task:
                task.position = position
                await task.save()


class ShoppingItemService:
    """Service for shopping item operations"""
    
    def __init__(self, database: Database):
        self.database = database
    
    async def get_items_by_list(self, list_id: UUID, user_id: UUID) -> ListType[ShoppingItem]:
        """Get all shopping items for a specific list and user"""
        return await ShoppingItem.query.filter(list=list_id, user_id=user_id).all().order_by("position")
    
    async def get_item_by_id(self, item_id: UUID, user_id: UUID) -> ShoppingItem:
        """Get a shopping item by ID for a specific user"""
        item = await ShoppingItem.query.filter(id=item_id, user_id=user_id).first()
        if not item:
            raise ObjectNotFound("Shopping item not found")
        return item
    
    async def create_item(self, item_data: dict, user_id: UUID, list_id: UUID) -> ShoppingItem:
        data = dict(item_data)
        data['user_id'] = user_id
        data['list'] = list_id
        return await ShoppingItem.query.create(**data)
    
    async def update_item(self, item_id: UUID, item_data: ShoppingItemUpdate, user_id: UUID) -> ShoppingItem:
        """Update a shopping item for a specific user"""
        item = await self.get_item_by_id(item_id, user_id)
        update_data = {k: v for k, v in item_data.model_dump().items() if v is not None}
        await item.update(**update_data)
        # Reload the item to ensure user relation is loaded
        return await self.get_item_by_id(item_id, user_id)
    
    async def delete_item(self, item_id: UUID, user_id: UUID) -> bool:
        """Delete a shopping item for a specific user"""
        item = await self.get_item_by_id(item_id, user_id)
        await item.delete()
        return True
    
    async def toggle_item(self, item_id: UUID, user_id: UUID) -> ShoppingItem:
        """Toggle shopping item completion status for a specific user"""
        item = await self.get_item_by_id(item_id, user_id)
        item.checked = not item.checked
        await item.save()
        # Reload the item to ensure user relation is loaded
        return await self.get_item_by_id(item_id, user_id)
    
    async def reorder_items(self, list_id: UUID, reorder_data: ReorderRequest, user_id: UUID) -> None:
        """Reorder shopping items for a list by updating their positions."""
        item_ids = reorder_data.item_ids
        items = await ShoppingItem.query.filter(list=list_id, user_id=user_id).all()
        item_map = {str(item.id): item for item in items}
        for position, item_id in enumerate(item_ids):
            item = item_map.get(str(item_id))
            if item:
                item.position = position
                await item.save()


class SearchService:
    """Service for search operations"""
    
    def __init__(self, database: Database):
        self.database = database
    
    async def search_all(self, query: str, user_id: UUID) -> dict:
        """Search across all user content"""
        # Search in lists
        lists = await List.query.filter(
            user_id=user_id,
            title__icontains=query
        ).all()
        
        # Search in tasks
        tasks = await Task.query.filter(
            user_id=user_id,
            title__icontains=query
        ).all()
        
        # Search in shopping items
        shopping_items = await ShoppingItem.query.filter(
            user_id=user_id,
            title__icontains=query
        ).all()
        
        return {
            "lists": lists,
            "tasks": tasks,
            "shopping_items": shopping_items
        } 