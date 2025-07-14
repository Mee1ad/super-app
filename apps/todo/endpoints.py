# endpoints for todo app 
from typing import List as ListType
from uuid import UUID

from esmerald import get, post, put, delete, HTTPException, status, Request
from esmerald.exceptions import NotFound
from edgy.exceptions import ObjectNotFound

from .models import Task, ShoppingItem
from .schemas import (
    ListCreate, ListUpdate, ListResponse,
    TaskCreate, TaskUpdate, TaskResponse,
    ShoppingItemCreate, ShoppingItemUpdate, ShoppingItemResponse,
    ReorderRequest, SearchResponse
)
from .services import ListService, TaskService, ShoppingItemService, SearchService
from db.session import database
from core.dependencies import get_current_user_id

# Dependency injection
from db.session import database

list_service = ListService(database)
task_service = TaskService(database)
shopping_item_service = ShoppingItemService(database)
search_service = SearchService(database)


@get(
    path="/api/lists",
    tags=["Lists"],
    summary="Get all lists",
    description="Retrieve all lists for the authenticated user. Supports pagination and filtering by type."
)
async def get_lists(request: Request) -> ListType[ListResponse]:
    """
    Retrieve all lists for the authenticated user.
    
    This endpoint returns all lists (both task and shopping lists) ordered by
    creation date (newest first). The response includes basic list information
    without the nested items for performance.
    
    Returns:
        List[ListResponse]: Array of lists with basic information
        
    Raises:
        401: Authentication required - Include valid Authorization header
        429: Rate limit exceeded - Too many requests, retry after delay
    """
    user_id = await get_current_user_id(request)
    lists = await list_service.get_all_lists(user_id)
    return [ListResponse.model_validate_from_orm(list_obj) for list_obj in lists]


@post(
    path="/api/lists",
    tags=["Lists"],
    summary="Create a new list",
    description="Create a new list for the authenticated user."
)
async def create_list(
    request: Request,
    data: ListCreate
) -> ListResponse:
    """
    Create a new list for the authenticated user.
    
    Args:
        data: List creation data
        
    Returns:
        ListResponse: Created list information
        
    Raises:
        400: Bad request - Invalid list data
        401: Authentication required - Include valid Authorization header
        422: Validation error - Invalid input data
    """
    user_id = await get_current_user_id(request)
    list_obj = await list_service.create_list(data, user_id)
    return ListResponse.model_validate_from_orm(list_obj)


@put(
    path="/api/lists/{list_id:uuid}",
    tags=["Lists"],
    summary="Update a list",
    description="Update an existing list for the authenticated user."
)
async def update_list(
    request: Request,
    list_id: UUID,
    data: ListUpdate
) -> ListResponse:
    """
    Update an existing list for the authenticated user.
    
    Args:
        list_id: ID of the list to update
        data: List update data
        
    Returns:
        ListResponse: Updated list information
        
    Raises:
        400: Bad request - Invalid list data
        401: Authentication required - Include valid Authorization header
        404: Not found - List not found
        422: Validation error - Invalid input data
    """
    user_id = await get_current_user_id(request)
    try:
        list_obj = await list_service.update_list(list_id, data, user_id)
        return ListResponse.model_validate_from_orm(list_obj)
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="List not found")


@delete(
    path="/api/lists/{list_id:uuid}",
    tags=["Lists"],
    summary="Delete a list",
    description="Delete a list and all its items for the authenticated user.",
    status_code=200
)
async def delete_list(
    request: Request,
    list_id: UUID
) -> dict:
    """
    Delete a list and all its items for the authenticated user.
    
    Args:
        list_id: ID of the list to delete
        
    Returns:
        dict: Success message
        
    Raises:
        401: Authentication required - Include valid Authorization header
        404: Not found - List not found
    """
    user_id = await get_current_user_id(request)
    try:
        await list_service.delete_list(list_id, user_id)
        return {"message": "List deleted successfully"}
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="List not found")


@get(
    path="/api/lists/{list_id:uuid}/tasks",
    tags=["Tasks"],
    summary="Get tasks for a list",
    description="Retrieve all tasks for a specific list belonging to the authenticated user."
)
async def get_tasks(
    request: Request,
    list_id: UUID
) -> ListType[TaskResponse]:
    """
    Retrieve all tasks for a specific list belonging to the authenticated user.
    
    Args:
        list_id: ID of the list
        
    Returns:
        List[TaskResponse]: Array of tasks
        
    Raises:
        401: Authentication required - Include valid Authorization header
        404: Not found - List not found
    """
    user_id = await get_current_user_id(request)
    try:
        parent_list = await list_service.get_list_by_id(list_id, user_id)
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="List not found")
    tasks = await task_service.get_tasks_by_list(list_id, user_id)
    return [TaskResponse.model_validate_from_orm(task) for task in tasks]


@post(
    path="/api/lists/{list_id:uuid}/tasks",
    tags=["Tasks"],
    summary="Create a new task",
    description="Create a new task in a list for the authenticated user."
)
async def create_task(
    request: Request,
    list_id: UUID,
    data: TaskCreate
) -> TaskResponse:
    user_id = await get_current_user_id(request)
    try:
        parent_list = await list_service.get_list_by_id(list_id, user_id)
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="List not found")
    task_data = data.model_dump()
    task = await task_service.create_task(task_data, user_id, list_id)
    return TaskResponse.model_validate_from_orm(task)


@put(
    path="/api/lists/{list_id:uuid}/tasks/{task_id:uuid}",
    tags=["Tasks"],
    summary="Update a task",
    description="Update an existing task for the authenticated user."
)
async def update_task(
    request: Request,
    list_id: UUID,
    task_id: UUID,
    data: TaskUpdate
) -> TaskResponse:
    """
    Update an existing task for the authenticated user.
    
    Args:
        list_id: ID of the list containing the task
        task_id: ID of the task to update
        data: Task update data
        
    Returns:
        TaskResponse: Updated task information
        
    Raises:
        400: Bad request - Invalid task data
        401: Authentication required - Include valid Authorization header
        404: Not found - Task not found
        422: Validation error - Invalid input data
    """
    user_id = await get_current_user_id(request)
    try:
        task = await task_service.update_task(task_id, data, user_id)
        return TaskResponse.model_validate_from_orm(task)
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Task not found")


@delete(
    path="/api/lists/{list_id:uuid}/tasks/{task_id:uuid}",
    tags=["Tasks"],
    summary="Delete a task",
    description="Delete a task for the authenticated user.",
    status_code=200
)
async def delete_task(
    request: Request,
    list_id: UUID,
    task_id: UUID
) -> dict:
    """
    Delete a task for the authenticated user.
    
    Args:
        list_id: ID of the list containing the task
        task_id: ID of the task to delete
        
    Returns:
        dict: Success message
        
    Raises:
        401: Authentication required - Include valid Authorization header
        404: Not found - Task not found
    """
    user_id = await get_current_user_id(request)
    try:
        await task_service.delete_task(task_id, user_id)
        return {"message": "Task deleted successfully"}
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Task not found")


@put(
    path="/api/lists/{list_id:uuid}/tasks/{task_id:uuid}/toggle",
    tags=["Tasks"],
    summary="Toggle task completion",
    description="Toggle the completion status of a task for the authenticated user."
)
async def toggle_task(
    request: Request,
    list_id: UUID,
    task_id: UUID
) -> TaskResponse:
    """
    Toggle the completion status of a task for the authenticated user.
    
    Args:
        list_id: ID of the list containing the task
        task_id: ID of the task to toggle
        
    Returns:
        TaskResponse: Updated task information
        
    Raises:
        401: Authentication required - Include valid Authorization header
        404: Not found - Task not found
    """
    user_id = await get_current_user_id(request)
    try:
        task = await task_service.toggle_task(task_id, user_id)
        return TaskResponse.model_validate_from_orm(task)
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Task not found")


@put(
    path="/api/lists/{list_id:uuid}/tasks/reorder",
    tags=["Tasks"],
    summary="Reorder tasks",
    description="Reorder tasks in a list for the authenticated user."
)
async def reorder_tasks(
    request: Request,
    list_id: UUID,
    data: ReorderRequest
) -> dict:
    """
    Reorder tasks in a list for the authenticated user.
    """
    user_id = await get_current_user_id(request)
    await task_service.reorder_tasks(list_id, data, user_id)
    return {"message": "Tasks reordered successfully"}


@get(
    path="/api/lists/{list_id:uuid}/items",
    tags=["Shopping Items"],
    summary="Get shopping items for a list",
    description="Retrieve all shopping items for a specific list belonging to the authenticated user."
)
async def get_items(
    request: Request,
    list_id: UUID
) -> ListType[ShoppingItemResponse]:
    """
    Retrieve all shopping items for a specific list belonging to the authenticated user.
    
    Args:
        list_id: ID of the list
        
    Returns:
        List[ShoppingItemResponse]: Array of shopping items
        
    Raises:
        401: Authentication required - Include valid Authorization header
        404: Not found - List not found
    """
    user_id = await get_current_user_id(request)
    try:
        parent_list = await list_service.get_list_by_id(list_id, user_id)
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="List not found")
    items = await shopping_item_service.get_items_by_list(list_id, user_id)
    return [ShoppingItemResponse.model_validate_from_orm(item) for item in items]


@post(
    path="/api/lists/{list_id:uuid}/items",
    tags=["Shopping Items"],
    summary="Create a new shopping item",
    description="Create a new shopping item in a list for the authenticated user."
)
async def create_item(
    request: Request,
    list_id: UUID,
    data: ShoppingItemCreate
) -> ShoppingItemResponse:
    user_id = await get_current_user_id(request)
    try:
        parent_list = await list_service.get_list_by_id(list_id, user_id)
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="List not found")
    item_data = data.model_dump()
    item = await shopping_item_service.create_item(item_data, user_id, list_id)
    return ShoppingItemResponse.model_validate_from_orm(item)


@put(
    path="/api/lists/{list_id:uuid}/items/{item_id:uuid}",
    tags=["Shopping Items"],
    summary="Update a shopping item",
    description="Update an existing shopping item for the authenticated user."
)
async def update_item(
    request: Request,
    list_id: UUID,
    item_id: UUID,
    data: ShoppingItemUpdate
) -> ShoppingItemResponse:
    """
    Update an existing shopping item for the authenticated user.
    
    Args:
        list_id: ID of the list containing the item
        item_id: ID of the item to update
        data: Shopping item update data
        
    Returns:
        ShoppingItemResponse: Updated shopping item information
        
    Raises:
        400: Bad request - Invalid item data
        401: Authentication required - Include valid Authorization header
        404: Not found - Item not found
        422: Validation error - Invalid input data
    """
    user_id = await get_current_user_id(request)
    try:
        item = await shopping_item_service.update_item(item_id, data, user_id)
        return ShoppingItemResponse.model_validate_from_orm(item)
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Shopping item not found")


@delete(
    path="/api/lists/{list_id:uuid}/items/{item_id:uuid}",
    tags=["Shopping Items"],
    summary="Delete a shopping item",
    description="Delete a shopping item for the authenticated user.",
    status_code=200
)
async def delete_item(
    request: Request,
    list_id: UUID,
    item_id: UUID
) -> dict:
    """
    Delete a shopping item for the authenticated user.
    
    Args:
        list_id: ID of the list containing the item
        item_id: ID of the item to delete
        
    Returns:
        dict: Success message
        
    Raises:
        401: Authentication required - Include valid Authorization header
        404: Not found - Item not found
    """
    user_id = await get_current_user_id(request)
    try:
        await shopping_item_service.delete_item(item_id, user_id)
        return {"message": "Shopping item deleted successfully"}
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Shopping item not found")


@put(
    path="/api/lists/{list_id:uuid}/items/{item_id:uuid}/toggle",
    tags=["Shopping Items"],
    summary="Toggle shopping item completion",
    description="Toggle the completion status of a shopping item for the authenticated user."
)
async def toggle_item(
    request: Request,
    list_id: UUID,
    item_id: UUID
) -> ShoppingItemResponse:
    """
    Toggle the completion status of a shopping item for the authenticated user.
    
    Args:
        list_id: ID of the list containing the item
        item_id: ID of the item to toggle
        
    Returns:
        ShoppingItemResponse: Updated shopping item information
        
    Raises:
        401: Authentication required - Include valid Authorization header
        404: Not found - Item not found
    """
    user_id = await get_current_user_id(request)
    try:
        item = await shopping_item_service.toggle_item(item_id, user_id)
        return ShoppingItemResponse.model_validate_from_orm(item)
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Shopping item not found")


@put(
    path="/api/lists/{list_id:uuid}/items/reorder",
    tags=["Shopping Items"],
    summary="Reorder shopping items",
    description="Reorder shopping items in a list for the authenticated user."
)
async def reorder_items(
    request: Request,
    list_id: UUID,
    data: ReorderRequest
) -> dict:
    """
    Reorder shopping items in a list for the authenticated user.
    """
    user_id = await get_current_user_id(request)
    await shopping_item_service.reorder_items(list_id, data, user_id)
    return {"message": "Shopping items reordered successfully"}


@get(
    path="/api/search",
    tags=["Search"],
    summary="Search across all content",
    description="Search for lists, tasks, and shopping items across all user content. Minimum 2 characters required."
)
async def search(
    request: Request,
    q: str
) -> SearchResponse:
    """
    Search across all lists, tasks, and shopping items for the authenticated user.
    
    This endpoint performs a full-text search across all user content
    including lists, tasks, and shopping items. Results are grouped by type.
    
    Args:
        q: Search query string (minimum 3 characters)
        
    Returns:
        SearchResponse: Search results grouped by content type
        
    Raises:
        400: Bad request - Query too short (minimum 3 characters)
        401: Authentication required - Include valid Authorization header
        429: Rate limit exceeded - Too many requests, retry after delay
    """
    if len(q.strip()) < 3:
        raise HTTPException(status_code=400, detail="Search query must be at least 3 characters long")
    
    user_id = await get_current_user_id(request)
    results = await search_service.search_all(q, user_id)
    return SearchResponse(
        lists=[ListResponse.model_validate_from_orm(list_obj) for list_obj in results["lists"]],
        tasks=[TaskResponse.model_validate_from_orm(task) for task in results["tasks"]],
        shopping_items=[ShoppingItemResponse.model_validate_from_orm(item) for item in results["shopping_items"]]
    )

@get(
    path="/api/health",
    tags=["Health"],
    summary="Health check",
    description="Check the health status of the API service."
)
async def health_check() -> dict:
    """
    Check the health status of the API service.
    
    This endpoint provides a simple health check to verify that the API
    service is running and responsive. Used for monitoring and load balancing.
    
    Returns:
        dict: Health status information
    """
    return {
        "status": "healthy",
        "message": "Todo API is running",
        "version": "1.0.0"
    } 
