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
    
    async def get_all_lists(self) -> ListType[List]:
        """Get all lists ordered by creation date"""
        return await List.query.all().order_by("-created_at")
    
    async def get_list_by_id(self, list_id: UUID) -> List:
        """Get a list by ID"""
        list_obj = await List.query.get(id=list_id)
        if not list_obj:
            raise ObjectNotFound("List not found")
        return list_obj
    
    async def create_list(self, list_data: ListCreate) -> List:
        """Create a new list"""
        return await List.query.create(**list_data.dict())
    
    async def update_list(self, list_id: UUID, list_data: ListUpdate) -> List:
        """Update a list"""
        list_obj = await self.get_list_by_id(list_id)
        update_data = {k: v for k, v in list_data.dict().items() if v is not None}
        return await list_obj.update(**update_data)
    
    async def delete_list(self, list_id: UUID) -> bool:
        """Delete a list and all its items"""
        list_obj = await self.get_list_by_id(list_id)
        await list_obj.delete()
        return True


class TaskService:
    """Service for task operations"""
    
    def __init__(self, database: Database):
        self.database = database
    
    async def get_tasks_by_list(self, list_id: UUID) -> ListType[Task]:
        """Get all tasks for a list ordered by position"""
        return await Task.query.filter(list=list_id).order_by("position")
    
    async def get_task_by_id(self, task_id: UUID) -> Task:
        """Get a task by ID"""
        task = await Task.query.get(id=task_id)
        if not task:
            raise ObjectNotFound("Task not found")
        return task
    
    async def create_task(self, list_id: UUID, task_data: TaskCreate) -> Task:
        """Create a new task in a list"""
        # Get the highest position in the list
        tasks = await Task.query.filter(list=list_id).order_by("-position").limit(1)
        max_position = tasks[0].position if tasks else 0
        task_data_dict = task_data.dict()
        task_data_dict["position"] = max_position + 1
        task_data_dict["list"] = list_id
        
        return await Task.query.create(**task_data_dict)
    
    async def update_task(self, task_id: UUID, task_data: TaskUpdate) -> Task:
        """Update a task"""
        task = await self.get_task_by_id(task_id)
        update_data = {k: v for k, v in task_data.dict().items() if v is not None}
        return await task.update(**update_data)
    
    async def delete_task(self, task_id: UUID) -> bool:
        """Delete a task"""
        task = await self.get_task_by_id(task_id)
        await task.delete()
        return True
    
    async def toggle_task(self, task_id: UUID) -> Task:
        """Toggle task completion status"""
        task = await self.get_task_by_id(task_id)
        return await task.update(checked=not task.checked)
    
    async def reorder_tasks(self, list_id: UUID, item_ids: ListType[UUID]) -> ListType[Task]:
        """Reorder tasks by updating their positions"""
        tasks = []
        for position, task_id in enumerate(item_ids, 1):
            task = await self.get_task_by_id(task_id)
            if task.list != list_id:
                raise ValueError("Task does not belong to the specified list")
            updated_task = await task.update(position=position)
            tasks.append(updated_task)
        return tasks


class ShoppingItemService:
    """Service for shopping item operations"""
    
    def __init__(self, database: Database):
        self.database = database
    
    async def get_items_by_list(self, list_id: UUID) -> ListType[ShoppingItem]:
        """Get all shopping items for a list ordered by position"""
        return await ShoppingItem.query.filter(list=list_id).order_by("position")
    
    async def get_item_by_id(self, item_id: UUID) -> ShoppingItem:
        """Get a shopping item by ID"""
        item = await ShoppingItem.query.get(id=item_id)
        if not item:
            raise ObjectNotFound("Shopping item not found")
        return item
    
    async def create_item(self, list_id: UUID, item_data: ShoppingItemCreate) -> ShoppingItem:
        """Create a new shopping item in a list"""
        # Get the highest position in the list
        items = await ShoppingItem.query.filter(list=list_id).order_by("-position").limit(1)
        max_position = items[0].position if items else 0
        item_data_dict = item_data.dict()
        item_data_dict["position"] = max_position + 1
        item_data_dict["list"] = list_id
        
        return await ShoppingItem.query.create(**item_data_dict)
    
    async def update_item(self, item_id: UUID, item_data: ShoppingItemUpdate) -> ShoppingItem:
        """Update a shopping item"""
        item = await self.get_item_by_id(item_id)
        update_data = {k: v for k, v in item_data.dict().items() if v is not None}
        return await item.update(**update_data)
    
    async def delete_item(self, item_id: UUID) -> bool:
        """Delete a shopping item"""
        item = await self.get_item_by_id(item_id)
        await item.delete()
        return True
    
    async def toggle_item(self, item_id: UUID) -> ShoppingItem:
        """Toggle shopping item completion status"""
        item = await self.get_item_by_id(item_id)
        return await item.update(checked=not item.checked)
    
    async def reorder_items(self, list_id: UUID, item_ids: ListType[UUID]) -> ListType[ShoppingItem]:
        """Reorder shopping items by updating their positions"""
        items = []
        for position, item_id in enumerate(item_ids, 1):
            item = await self.get_item_by_id(item_id)
            if item.list != list_id:
                raise ValueError("Shopping item does not belong to the specified list")
            updated_item = await item.update(position=position)
            items.append(updated_item)
        return items


class SearchService:
    """Service for search operations"""
    
    def __init__(self, database: Database):
        self.database = database
    
    async def search_all(self, query: str) -> dict:
        """Search across all lists, tasks, and shopping items"""
        # Search in lists
        lists = await List.query.filter(title__icontains=query).all()
        
        # Search in tasks
        tasks = await Task.query.filter(title__icontains=query).all()
        
        # Search in shopping items
        shopping_items = await ShoppingItem.query.filter(title__icontains=query).all()
        
        return {
            "lists": lists,
            "tasks": tasks,
            "shopping_items": shopping_items
        } 