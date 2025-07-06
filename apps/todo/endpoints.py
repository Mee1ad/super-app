# endpoints for todo app 
from typing import List as ListType
from uuid import UUID

from esmerald import get, post, put, delete
from esmerald.exceptions import HTTPException, NotFound
from edgy import Database
from edgy.exceptions import ObjectNotFound

from .models import List, Task, ShoppingItem
from .schemas import (
    ListCreate, ListUpdate, ListResponse, TaskCreate, TaskUpdate, TaskResponse,
    ShoppingItemCreate, ShoppingItemUpdate, ShoppingItemResponse,
    ReorderRequest, SearchResponse
)
from .services import ListService, TaskService, ShoppingItemService, SearchService
from db.session import database

list_service = ListService(database)
task_service = TaskService(database)
shopping_item_service = ShoppingItemService(database)
search_service = SearchService(database)

@get(path="/api/lists")
async def get_lists() -> ListType[ListResponse]:
    lists = await list_service.get_all_lists()
    return [ListResponse.from_orm(list_obj) for list_obj in lists]

@post(path="/api/lists")
async def create_list(data: ListCreate) -> ListResponse:
    list_obj = await list_service.create_list(data)
    return ListResponse.from_orm(list_obj)

@put(path="/api/lists/{list_id:uuid}")
async def update_list(list_id: UUID, data: ListUpdate) -> ListResponse:
    list_obj = await list_service.update_list(list_id, data)
    return ListResponse.from_orm(list_obj)

@delete(path="/api/lists/{list_id:uuid}", status_code=200)
async def delete_list(list_id: UUID) -> dict:
    await list_service.delete_list(list_id)
    return {"message": "List deleted successfully"}

@get(path="/api/lists/{list_id:uuid}/tasks")
async def get_tasks(list_id: UUID) -> ListType[TaskResponse]:
    tasks = await task_service.get_tasks_by_list(list_id)
    return [TaskResponse.from_orm(task) for task in tasks]

@post(path="/api/lists/{list_id:uuid}/tasks")
async def create_task(list_id: UUID, data: TaskCreate) -> TaskResponse:
    task = await task_service.create_task(list_id, data)
    return TaskResponse.from_orm(task)

@put(path="/api/lists/{list_id:uuid}/tasks/{task_id:uuid}")
async def update_task(list_id: UUID, task_id: UUID, data: TaskUpdate) -> TaskResponse:
    task = await task_service.update_task(task_id, data)
    return TaskResponse.from_orm(task)

@delete(path="/api/lists/{list_id:uuid}/tasks/{task_id:uuid}", status_code=200)
async def delete_task(list_id: UUID, task_id: UUID) -> dict:
    await task_service.delete_task(task_id)
    return {"message": "Task deleted successfully"}

@put(path="/api/lists/{list_id:uuid}/tasks/{task_id:uuid}/toggle")
async def toggle_task(list_id: UUID, task_id: UUID) -> TaskResponse:
    task = await task_service.toggle_task(task_id)
    return TaskResponse.from_orm(task)

@put(path="/api/lists/{list_id:uuid}/tasks/reorder")
async def reorder_tasks(list_id: UUID, data: ReorderRequest) -> ListType[TaskResponse]:
    tasks = await task_service.reorder_tasks(list_id, data.item_ids)
    return [TaskResponse.from_orm(task) for task in tasks]

@get(path="/api/lists/{list_id:uuid}/items")
async def get_items(list_id: UUID) -> ListType[ShoppingItemResponse]:
    items = await shopping_item_service.get_items_by_list(list_id)
    return [ShoppingItemResponse.from_orm(item) for item in items]

@post(path="/api/lists/{list_id:uuid}/items")
async def create_item(list_id: UUID, data: ShoppingItemCreate) -> ShoppingItemResponse:
    item = await shopping_item_service.create_item(list_id, data)
    return ShoppingItemResponse.from_orm(item)

@put(path="/api/lists/{list_id:uuid}/items/{item_id:uuid}")
async def update_item(list_id: UUID, item_id: UUID, data: ShoppingItemUpdate) -> ShoppingItemResponse:
    item = await shopping_item_service.update_item(item_id, data)
    return ShoppingItemResponse.from_orm(item)

@delete(path="/api/lists/{list_id:uuid}/items/{item_id:uuid}", status_code=200)
async def delete_item(list_id: UUID, item_id: UUID) -> dict:
    await shopping_item_service.delete_item(item_id)
    return {"message": "Shopping item deleted successfully"}

@put(path="/api/lists/{list_id:uuid}/items/{item_id:uuid}/toggle")
async def toggle_item(list_id: UUID, item_id: UUID) -> ShoppingItemResponse:
    item = await shopping_item_service.toggle_item(item_id)
    return ShoppingItemResponse.from_orm(item)

@put(path="/api/lists/{list_id:uuid}/items/reorder")
async def reorder_items(list_id: UUID, data: ReorderRequest) -> ListType[ShoppingItemResponse]:
    items = await shopping_item_service.reorder_items(list_id, data.item_ids)
    return [ShoppingItemResponse.from_orm(item) for item in items]

@get(path="/api/search")
async def search(q: str) -> SearchResponse:
    results = await search_service.search_all(q)
    return SearchResponse(
        lists=[ListResponse.from_orm(list_obj) for list_obj in results["lists"]],
        tasks=[TaskResponse.from_orm(task) for task in results["tasks"]],
        shopping_items=[ShoppingItemResponse.from_orm(item) for item in results["shopping_items"]]
    ) 
