# endpoints for todo app 
from typing import List
from uuid import UUID

from esmerald import APIGateHandler, Gateway, get, post, put, delete
from esmerald.exceptions import APIException, NotFound, BadRequest
from edgy import Database
from edgy.exceptions import ObjectNotFound

from .models import List, Task, ShoppingItem
from .schemas import (
    ListCreate, ListUpdate, ListResponse, TaskCreate, TaskUpdate, TaskResponse,
    ShoppingItemCreate, ShoppingItemUpdate, ShoppingItemResponse,
    ReorderRequest, SearchResponse
)
from .services import ListService, TaskService, ShoppingItemService, SearchService


class ListHandler(APIGateHandler):
    """Handler for list operations"""
    
    def __init__(self, database: Database):
        self.database = database
        self.service = ListService(database)
    
    @get(path="/api/lists", summary="Get all lists")
    async def get_lists(self) -> List[ListResponse]:
        """Get all lists"""
        try:
            lists = await self.service.get_all_lists()
            return [ListResponse.from_orm(list_obj) for list_obj in lists]
        except Exception as e:
            raise APIException(detail=str(e))
    
    @post(path="/api/lists", summary="Create a new list")
    async def create_list(self, data: ListCreate) -> ListResponse:
        """Create a new list"""
        try:
            list_obj = await self.service.create_list(data)
            return ListResponse.from_orm(list_obj)
        except Exception as e:
            raise APIException(detail=str(e))
    
    @put(path="/api/lists/{list_id:uuid}", summary="Update a list")
    async def update_list(self, list_id: UUID, data: ListUpdate) -> ListResponse:
        """Update a list"""
        try:
            list_obj = await self.service.update_list(list_id, data)
            return ListResponse.from_orm(list_obj)
        except ObjectNotFound:
            raise NotFound(detail="List not found")
        except Exception as e:
            raise APIException(detail=str(e))
    
    @delete(path="/api/lists/{list_id:uuid}", summary="Delete a list")
    async def delete_list(self, list_id: UUID) -> dict:
        """Delete a list"""
        try:
            await self.service.delete_list(list_id)
            return {"message": "List deleted successfully"}
        except ObjectNotFound:
            raise NotFound(detail="List not found")
        except Exception as e:
            raise APIException(detail=str(e))


class TaskHandler(APIGateHandler):
    """Handler for task operations"""
    
    def __init__(self, database: Database):
        self.database = database
        self.service = TaskService(database)
    
    @get(path="/api/lists/{list_id:uuid}/tasks", summary="Get tasks for a list")
    async def get_tasks(self, list_id: UUID) -> List[TaskResponse]:
        """Get all tasks for a list"""
        try:
            tasks = await self.service.get_tasks_by_list(list_id)
            return [TaskResponse.from_orm(task) for task in tasks]
        except Exception as e:
            raise APIException(detail=str(e))
    
    @post(path="/api/lists/{list_id:uuid}/tasks", summary="Create a new task")
    async def create_task(self, list_id: UUID, data: TaskCreate) -> TaskResponse:
        """Create a new task in a list"""
        try:
            task = await self.service.create_task(list_id, data)
            return TaskResponse.from_orm(task)
        except Exception as e:
            raise APIException(detail=str(e))
    
    @put(path="/api/lists/{list_id:uuid}/tasks/{task_id:uuid}", summary="Update a task")
    async def update_task(self, list_id: UUID, task_id: UUID, data: TaskUpdate) -> TaskResponse:
        """Update a task"""
        try:
            task = await self.service.update_task(task_id, data)
            if task.list_id != list_id:
                raise BadRequest(detail="Task does not belong to the specified list")
            return TaskResponse.from_orm(task)
        except ObjectNotFound:
            raise NotFound(detail="Task not found")
        except Exception as e:
            raise APIException(detail=str(e))
    
    @delete(path="/api/lists/{list_id:uuid}/tasks/{task_id:uuid}", summary="Delete a task")
    async def delete_task(self, list_id: UUID, task_id: UUID) -> dict:
        """Delete a task"""
        try:
            task = await self.service.get_task_by_id(task_id)
            if task.list_id != list_id:
                raise BadRequest(detail="Task does not belong to the specified list")
            await self.service.delete_task(task_id)
            return {"message": "Task deleted successfully"}
        except ObjectNotFound:
            raise NotFound(detail="Task not found")
        except Exception as e:
            raise APIException(detail=str(e))
    
    @put(path="/api/lists/{list_id:uuid}/tasks/{task_id:uuid}/toggle", summary="Toggle task completion")
    async def toggle_task(self, list_id: UUID, task_id: UUID) -> TaskResponse:
        """Toggle task completion status"""
        try:
            task = await self.service.toggle_task(task_id)
            if task.list_id != list_id:
                raise BadRequest(detail="Task does not belong to the specified list")
            return TaskResponse.from_orm(task)
        except ObjectNotFound:
            raise NotFound(detail="Task not found")
        except Exception as e:
            raise APIException(detail=str(e))
    
    @put(path="/api/lists/{list_id:uuid}/tasks/reorder", summary="Reorder tasks")
    async def reorder_tasks(self, list_id: UUID, data: ReorderRequest) -> List[TaskResponse]:
        """Reorder tasks by updating their positions"""
        try:
            tasks = await self.service.reorder_tasks(list_id, data.item_ids)
            return [TaskResponse.from_orm(task) for task in tasks]
        except ValueError as e:
            raise BadRequest(detail=str(e))
        except Exception as e:
            raise APIException(detail=str(e))


class ShoppingItemHandler(APIGateHandler):
    """Handler for shopping item operations"""
    
    def __init__(self, database: Database):
        self.database = database
        self.service = ShoppingItemService(database)
    
    @get(path="/api/lists/{list_id:uuid}/items", summary="Get shopping items for a list")
    async def get_items(self, list_id: UUID) -> List[ShoppingItemResponse]:
        """Get all shopping items for a list"""
        try:
            items = await self.service.get_items_by_list(list_id)
            return [ShoppingItemResponse.from_orm(item) for item in items]
        except Exception as e:
            raise APIException(detail=str(e))
    
    @post(path="/api/lists/{list_id:uuid}/items", summary="Create a new shopping item")
    async def create_item(self, list_id: UUID, data: ShoppingItemCreate) -> ShoppingItemResponse:
        """Create a new shopping item in a list"""
        try:
            item = await self.service.create_item(list_id, data)
            return ShoppingItemResponse.from_orm(item)
        except Exception as e:
            raise APIException(detail=str(e))
    
    @put(path="/api/lists/{list_id:uuid}/items/{item_id:uuid}", summary="Update a shopping item")
    async def update_item(self, list_id: UUID, item_id: UUID, data: ShoppingItemUpdate) -> ShoppingItemResponse:
        """Update a shopping item"""
        try:
            item = await self.service.update_item(item_id, data)
            if item.list_id != list_id:
                raise BadRequest(detail="Shopping item does not belong to the specified list")
            return ShoppingItemResponse.from_orm(item)
        except ObjectNotFound:
            raise NotFound(detail="Shopping item not found")
        except Exception as e:
            raise APIException(detail=str(e))
    
    @delete(path="/api/lists/{list_id:uuid}/items/{item_id:uuid}", summary="Delete a shopping item")
    async def delete_item(self, list_id: UUID, item_id: UUID) -> dict:
        """Delete a shopping item"""
        try:
            item = await self.service.get_item_by_id(item_id)
            if item.list_id != list_id:
                raise BadRequest(detail="Shopping item does not belong to the specified list")
            await self.service.delete_item(item_id)
            return {"message": "Shopping item deleted successfully"}
        except ObjectNotFound:
            raise NotFound(detail="Shopping item not found")
        except Exception as e:
            raise APIException(detail=str(e))
    
    @put(path="/api/lists/{list_id:uuid}/items/{item_id:uuid}/toggle", summary="Toggle shopping item completion")
    async def toggle_item(self, list_id: UUID, item_id: UUID) -> ShoppingItemResponse:
        """Toggle shopping item completion status"""
        try:
            item = await self.service.toggle_item(item_id)
            if item.list_id != list_id:
                raise BadRequest(detail="Shopping item does not belong to the specified list")
            return ShoppingItemResponse.from_orm(item)
        except ObjectNotFound:
            raise NotFound(detail="Shopping item not found")
        except Exception as e:
            raise APIException(detail=str(e))
    
    @put(path="/api/lists/{list_id:uuid}/items/reorder", summary="Reorder shopping items")
    async def reorder_items(self, list_id: UUID, data: ReorderRequest) -> List[ShoppingItemResponse]:
        """Reorder shopping items by updating their positions"""
        try:
            items = await self.service.reorder_items(list_id, data.item_ids)
            return [ShoppingItemResponse.from_orm(item) for item in items]
        except ValueError as e:
            raise BadRequest(detail=str(e))
        except Exception as e:
            raise APIException(detail=str(e))


class SearchHandler(APIGateHandler):
    """Handler for search operations"""
    
    def __init__(self, database: Database):
        self.database = database
        self.service = SearchService(database)
    
    @get(path="/api/search", summary="Search across all entities")
    async def search(self, q: str) -> SearchResponse:
        """Search across all lists, tasks, and shopping items"""
        try:
            if not q or len(q.strip()) < 2:
                raise BadRequest(detail="Search query must be at least 2 characters long")
            
            results = await self.service.search_all(q.strip())
            return SearchResponse(
                lists=[ListResponse.from_orm(list_obj) for list_obj in results["lists"]],
                tasks=[TaskResponse.from_orm(task) for task in results["tasks"]],
                shopping_items=[ShoppingItemResponse.from_orm(item) for item in results["shopping_items"]]
            )
        except BadRequest:
            raise
        except Exception as e:
            raise APIException(detail=str(e)) 