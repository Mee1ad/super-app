# endpoints for todo app 
from typing import List as ListType
from uuid import UUID

from esmerald import get, post, put, delete, HTTPException, status
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
async def get_lists() -> ListType[ListResponse]:
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
    lists = await list_service.get_all_lists()
    return [ListResponse.model_validate(list_obj) for list_obj in lists]

@post(
    path="/api/lists",
    tags=["Lists"],
    summary="Create a new list",
    description="Create a new todo or shopping list. The list type determines whether it will contain tasks or shopping items."
)
async def create_list(data: ListCreate) -> ListResponse:
    """
    Create a new todo or shopping list.
    
    This endpoint creates a new list with the specified type and properties.
    The list type determines whether it will contain tasks (for todo lists)
    or shopping items (for shopping lists).
    
    Args:
        data: ListCreate schema containing list details
        
    Returns:
        ListResponse: The created list with generated ID and timestamps
        
    Raises:
        400: Bad request - Invalid request format or missing required fields
        401: Authentication required - Include valid Authorization header
        422: Validation error - Required fields missing or invalid values
        429: Rate limit exceeded - Too many requests, retry after delay
    """
    list_obj = await list_service.create_list(data)
    return ListResponse.model_validate(list_obj)

@put(
    path="/api/lists/{list_id:uuid}",
    tags=["Lists"],
    summary="Update a list",
    description="Update an existing list's properties. Only provided fields will be updated."
)
async def update_list(list_id: UUID, data: ListUpdate) -> ListResponse:
    """
    Update an existing list's properties.
    
    This endpoint allows partial updates to a list. Only the fields provided
    in the request will be updated. The list type cannot be changed after creation.
    
    Args:
        list_id: UUID of the list to update
        data: ListUpdate schema containing fields to update
        
    Returns:
        ListResponse: The updated list with new timestamps
        
    Raises:
        400: Bad request - Invalid request format or missing required fields
        401: Authentication required - Include valid Authorization header
        404: List not found - List with specified ID does not exist
        422: Validation error - Provided fields contain invalid values
        429: Rate limit exceeded - Too many requests, retry after delay
    """
    try:
        list_obj = await list_service.update_list(list_id, data)
        return ListResponse.model_validate(list_obj)
    except ObjectNotFound:
        raise NotFound("List not found")

@delete(
    path="/api/lists/{list_id:uuid}",
    status_code=200,
    tags=["Lists"],
    summary="Delete a list",
    description="Delete a list and all its associated tasks or shopping items. This action cannot be undone."
)
async def delete_list(list_id: UUID) -> dict:
    """
    Delete a list and all its associated items.
    
    This endpoint permanently deletes a list and all its associated tasks
    or shopping items. This action cannot be undone.
    
    Args:
        list_id: UUID of the list to delete
        
    Returns:
        dict: Success message confirming deletion
        
    Raises:
        400: Bad request - Invalid UUID format
        401: Authentication required - Include valid Authorization header
        404: List not found - List with specified ID does not exist
        429: Rate limit exceeded - Too many requests, retry after delay
    """
    try:
        await list_service.delete_list(list_id)
        return {"message": "List deleted successfully"}
    except ObjectNotFound:
        raise NotFound("List not found")


# Task endpoints
@get(
    path="/api/lists/{list_id:uuid}/tasks",
    tags=["Tasks"],
    summary="Get tasks in a list",
    description="Retrieve all tasks in a specific list. Tasks are returned in their current order."
)
async def get_tasks(list_id: UUID) -> ListType[TaskResponse]:
    """
    Retrieve all tasks in a specific list.
    
    This endpoint returns all tasks belonging to the specified list.
    Tasks are returned in their current position order.
    
    Args:
        list_id: UUID of the list containing the tasks
        
    Returns:
        List[TaskResponse]: Array of tasks in their current order
        
    Raises:
        400: Bad request - Invalid UUID format
        401: Authentication required - Include valid Authorization header
        404: List not found - List with specified ID does not exist
        429: Rate limit exceeded - Too many requests, retry after delay
    """
    try:
        # Validate that the list exists
        await list_service.get_list_by_id(list_id)
        tasks = await task_service.get_tasks_by_list(list_id)
        return [TaskResponse.model_validate_from_orm(task) for task in tasks]
    except ObjectNotFound:
        raise NotFound("List not found")

@post(
    path="/api/lists/{list_id:uuid}/tasks",
    tags=["Tasks"],
    summary="Create a new task",
    description="Create a new task in a specific list. The task will be added to the end of the list by default."
)
async def create_task(list_id: UUID, data: TaskCreate) -> TaskResponse:
    """
    Create a new task in a specific list.
    
    This endpoint creates a new task and adds it to the specified list.
    The task will be positioned at the end of the list by default.
    
    Args:
        list_id: UUID of the list to add the task to
        data: TaskCreate schema containing task details
        
    Returns:
        TaskResponse: The created task with generated ID and timestamps
        
    Raises:
        400: Bad request - Invalid request format or missing required fields
        401: Authentication required - Include valid Authorization header
        404: List not found - List with specified ID does not exist
        422: Validation error - Required fields missing or invalid values
        429: Rate limit exceeded - Too many requests, retry after delay
    """
    try:
        # Validate that the list exists
        await list_service.get_list_by_id(list_id)
        task = await task_service.create_task(list_id, data)
        return TaskResponse.model_validate_from_orm(task)
    except ObjectNotFound:
        raise NotFound("List not found")

@put(
    path="/api/lists/{list_id:uuid}/tasks/{task_id:uuid}",
    tags=["Tasks"],
    summary="Update a task",
    description="Update an existing task's properties. Only provided fields will be updated."
)
async def update_task(list_id: UUID, task_id: UUID, data: TaskUpdate) -> TaskResponse:
    """
    Update an existing task's properties.
    
    This endpoint allows partial updates to a task. Only the fields provided
    in the request will be updated. Position changes will reorder the task in the list.
    
    Args:
        list_id: UUID of the list containing the task
        task_id: UUID of the task to update
        data: TaskUpdate schema containing fields to update
        
    Returns:
        TaskResponse: The updated task with new timestamps
        
    Raises:
        400: Bad request - Invalid request format or missing required fields
        401: Authentication required - Include valid Authorization header
        404: List or task not found - List or task with specified ID does not exist
        422: Validation error - Provided fields contain invalid values
        429: Rate limit exceeded - Too many requests, retry after delay
    """
    try:
        task = await task_service.update_task(task_id, data, list_id=list_id)
        return TaskResponse.model_validate_from_orm(task)
    except ObjectNotFound:
        raise NotFound("Task not found")

@delete(
    path="/api/lists/{list_id:uuid}/tasks/{task_id:uuid}",
    status_code=200,
    tags=["Tasks"],
    summary="Delete a task",
    description="Delete a specific task from a list. This action cannot be undone."
)
async def delete_task(list_id: UUID, task_id: UUID) -> dict:
    """
    Delete a specific task from a list.
    
    This endpoint permanently deletes a task from the specified list.
    This action cannot be undone.
    
    Args:
        list_id: UUID of the list containing the task
        task_id: UUID of the task to delete
        
    Returns:
        dict: Success message confirming deletion
        
    Raises:
        400: Bad request - Invalid UUID format
        401: Authentication required - Include valid Authorization header
        404: List or task not found - List or task with specified ID does not exist
        429: Rate limit exceeded - Too many requests, retry after delay
    """
    try:
        await task_service.delete_task(task_id)
        return {"message": "Task deleted successfully"}
    except ObjectNotFound:
        raise NotFound("Task not found")

@put(
    path="/api/lists/{list_id:uuid}/tasks/{task_id:uuid}/toggle",
    tags=["Tasks"],
    summary="Toggle task completion",
    description="Toggle the checked status of a task (complete/incomplete)."
)
async def toggle_task(list_id: UUID, task_id: UUID) -> TaskResponse:
    """
    Toggle the completion status of a task.
    
    This endpoint toggles the checked status of a task between true and false.
    This is a convenient way to mark tasks as complete or incomplete.
    
    Args:
        list_id: UUID of the list containing the task
        task_id: UUID of the task to toggle
        
    Returns:
        TaskResponse: The updated task with toggled checked status
        
    Raises:
        400: Bad request - Invalid UUID format
        401: Authentication required - Include valid Authorization header
        404: List or task not found - List or task with specified ID does not exist
        429: Rate limit exceeded - Too many requests, retry after delay
    """
    try:
        task = await task_service.toggle_task(task_id)
        return TaskResponse.model_validate_from_orm(task)
    except ObjectNotFound:
        raise NotFound("Task not found")

@put(
    path="/api/lists/{list_id:uuid}/tasks/reorder",
    tags=["Tasks"],
    summary="Reorder tasks",
    description="Reorder tasks in a list by providing their IDs in the desired order."
)
async def reorder_tasks(list_id: UUID, data: ReorderRequest) -> ListType[TaskResponse]:
    """
    Reorder tasks in a list.
    
    This endpoint allows bulk reordering of tasks by providing their IDs
    in the desired order. All tasks in the list should be included in the order.
    
    Args:
        list_id: UUID of the list containing the tasks
        data: ReorderRequest containing array of task IDs in desired order
        
    Returns:
        List[TaskResponse]: Array of tasks in their new order
        
    Raises:
        400: Bad request - Invalid request format or missing required fields
        401: Authentication required - Include valid Authorization header
        404: List not found - List with specified ID does not exist
        422: Validation error - Task IDs are invalid or missing
        429: Rate limit exceeded - Too many requests, retry after delay
    """
    try:
        tasks = await task_service.reorder_tasks(list_id, data.item_ids)
        return [TaskResponse.model_validate_from_orm(task) for task in tasks]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ObjectNotFound:
        raise NotFound("List or task not found")

@get(
    path="/api/lists/{list_id:uuid}/items",
    tags=["Shopping Items"],
    summary="Get shopping items in a list",
    description="Retrieve all shopping items in a specific list. Items are returned in their current order."
)
async def get_items(list_id: UUID) -> ListType[ShoppingItemResponse]:
    """
    Retrieve all shopping items in a specific list.
    
    This endpoint returns all shopping items belonging to the specified list.
    Items are returned in their current position order.
    
    Args:
        list_id: UUID of the list containing the shopping items
        
    Returns:
        List[ShoppingItemResponse]: Array of shopping items in their current order
        
    Raises:
        400: Bad request - Invalid UUID format
        401: Authentication required - Include valid Authorization header
        404: List not found - List with specified ID does not exist
        429: Rate limit exceeded - Too many requests, retry after delay
    """
    try:
        # Validate that the list exists
        await list_service.get_list_by_id(list_id)
        items = await shopping_item_service.get_items_by_list(list_id)
        return [ShoppingItemResponse.model_validate_from_orm(item) for item in items]
    except ObjectNotFound:
        raise NotFound("List not found")

@post(
    path="/api/lists/{list_id:uuid}/items",
    tags=["Shopping Items"],
    summary="Create a new shopping item",
    description="Create a new shopping item in a specific list. The item will be added to the end of the list by default."
)
async def create_item(list_id: UUID, data: ShoppingItemCreate) -> ShoppingItemResponse:
    """
    Create a new shopping item in a specific list.
    
    This endpoint creates a new shopping item and adds it to the specified list.
    The item will be positioned at the end of the list by default.
    
    Args:
        list_id: UUID of the list to add the shopping item to
        data: ShoppingItemCreate schema containing item details
        
    Returns:
        ShoppingItemResponse: The created shopping item with generated ID and timestamps
        
    Raises:
        400: Bad request - Invalid request format or missing required fields
        401: Authentication required - Include valid Authorization header
        404: List not found - List with specified ID does not exist
        422: Validation error - Required fields missing or invalid values
        429: Rate limit exceeded - Too many requests, retry after delay
    """
    try:
        # Validate that the list exists
        await list_service.get_list_by_id(list_id)
        item = await shopping_item_service.create_item(list_id, data)
        return ShoppingItemResponse.model_validate_from_orm(item)
    except ObjectNotFound:
        raise NotFound("List not found")

@put(
    path="/api/lists/{list_id:uuid}/items/{item_id:uuid}",
    tags=["Shopping Items"],
    summary="Update a shopping item",
    description="Update an existing shopping item's properties. Only provided fields will be updated."
)
async def update_item(list_id: UUID, item_id: UUID, data: ShoppingItemUpdate) -> ShoppingItemResponse:
    """
    Update an existing shopping item's properties.
    
    This endpoint allows partial updates to a shopping item. Only the fields provided
    in the request will be updated. Position changes will reorder the item in the list.
    
    Args:
        list_id: UUID of the list containing the shopping item
        item_id: UUID of the shopping item to update
        data: ShoppingItemUpdate schema containing fields to update
        
    Returns:
        ShoppingItemResponse: The updated shopping item with new timestamps
        
    Raises:
        400: Bad request - Invalid request format or missing required fields
        401: Authentication required - Include valid Authorization header
        404: List or shopping item not found - List or item with specified ID does not exist
        422: Validation error - Provided fields contain invalid values
        429: Rate limit exceeded - Too many requests, retry after delay
    """
    try:
        item = await shopping_item_service.update_item(item_id, data, list_id=list_id)
        return ShoppingItemResponse.model_validate_from_orm(item)
    except ObjectNotFound:
        raise NotFound("Shopping item not found")

@delete(
    path="/api/lists/{list_id:uuid}/items/{item_id:uuid}",
    status_code=200,
    tags=["Shopping Items"],
    summary="Delete a shopping item",
    description="Delete a specific shopping item from a list. This action cannot be undone."
)
async def delete_item(list_id: UUID, item_id: UUID) -> dict:
    """
    Delete a specific shopping item from a list.
    
    This endpoint permanently deletes a shopping item from the specified list.
    This action cannot be undone.
    
    Args:
        list_id: UUID of the list containing the shopping item
        item_id: UUID of the shopping item to delete
        
    Returns:
        dict: Success message confirming deletion
        
    Raises:
        400: Bad request - Invalid UUID format
        401: Authentication required - Include valid Authorization header
        404: List or shopping item not found - List or item with specified ID does not exist
        429: Rate limit exceeded - Too many requests, retry after delay
    """
    try:
        await shopping_item_service.delete_item(item_id)
        return {"message": "Shopping item deleted successfully"}
    except ObjectNotFound:
        raise NotFound("Shopping item not found")

@put(
    path="/api/lists/{list_id:uuid}/items/{item_id:uuid}/toggle",
    tags=["Shopping Items"],
    summary="Toggle shopping item completion",
    description="Toggle the checked status of a shopping item (purchased/not purchased)."
)
async def toggle_item(list_id: UUID, item_id: UUID) -> ShoppingItemResponse:
    """
    Toggle the completion status of a shopping item.
    
    This endpoint toggles the checked status of a shopping item between true and false.
    This is a convenient way to mark items as purchased or not purchased.
    
    Args:
        list_id: UUID of the list containing the shopping item
        item_id: UUID of the shopping item to toggle
        
    Returns:
        ShoppingItemResponse: The updated shopping item with toggled checked status
        
    Raises:
        400: Bad request - Invalid UUID format
        401: Authentication required - Include valid Authorization header
        404: List or shopping item not found - List or item with specified ID does not exist
        429: Rate limit exceeded - Too many requests, retry after delay
    """
    try:
        item = await shopping_item_service.toggle_item(item_id)
        return ShoppingItemResponse.model_validate_from_orm(item)
    except ObjectNotFound:
        raise NotFound("Shopping item not found")

@put(
    path="/api/lists/{list_id:uuid}/items/reorder",
    tags=["Shopping Items"],
    summary="Reorder shopping items",
    description="Reorder shopping items in a list by providing their IDs in the desired order."
)
async def reorder_items(list_id: UUID, data: ReorderRequest) -> ListType[ShoppingItemResponse]:
    """
    Reorder shopping items in a list.
    
    This endpoint allows bulk reordering of shopping items by providing their IDs
    in the desired order. All items in the list should be included in the order.
    
    Args:
        list_id: UUID of the list containing the shopping items
        data: ReorderRequest containing array of item IDs in desired order
        
    Returns:
        List[ShoppingItemResponse]: Array of shopping items in their new order
        
    Raises:
        400: Bad request - Invalid request format or missing required fields
        401: Authentication required - Include valid Authorization header
        404: List not found - List with specified ID does not exist
        422: Validation error - Item IDs are invalid or missing
        429: Rate limit exceeded - Too many requests, retry after delay
    """
    try:
        items = await shopping_item_service.reorder_items(list_id, data.item_ids)
        return [ShoppingItemResponse.model_validate_from_orm(item) for item in items]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ObjectNotFound:
        raise NotFound("List or shopping item not found")

@get(
    path="/api/search",
    tags=["Search"],
    summary="Search across all content",
    description="Search for lists, tasks, and shopping items across all user content. Minimum 2 characters required."
)
async def search(q: str) -> SearchResponse:
    """
    Search across all lists, tasks, and shopping items.
    
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
    
    results = await search_service.search_all(q)
    return SearchResponse(
        lists=[ListResponse.model_validate(list_obj) for list_obj in results["lists"]],
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
