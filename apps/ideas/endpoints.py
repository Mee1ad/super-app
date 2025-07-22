# endpoints for ideas app 
from typing import List as ListType, Optional
from uuid import UUID

from esmerald import get, post, put, delete, HTTPException, status, Query, Request
from esmerald.exceptions import NotFound
from edgy.exceptions import ObjectNotFound

from .models import Category, Idea
from .schemas import (
    CategoryCreate, CategoryUpdate, CategoryResponse, CategoriesResponse,
    IdeaCreate, IdeaUpdate, IdeaResponse, IdeasResponse, PaginationMeta
)
from .services import CategoryService, IdeaService
from db.session import database
from core.dependencies import get_current_user_id

# Dependency injection
category_service = CategoryService(database)
idea_service = IdeaService(database)


@get(
    tags=["Categories"],
    summary="Get all categories",
    description="Retrieve all available categories for organizing ideas."
)
async def get_categories() -> CategoriesResponse:
    """
    Retrieve all available categories.
    
    This endpoint returns all categories that can be used to organize ideas.
    Categories are returned in alphabetical order by name.
    
    Returns:
        CategoriesResponse: Array of categories with id, name, and emoji
        
    Raises:
        401: Authentication required - Include valid Authorization header
        429: Rate limit exceeded - Too many requests, retry after delay
    """
    categories = await category_service.get_all_categories()
    return CategoriesResponse(
        categories=[CategoryResponse.model_validate(category) for category in categories]
    )


@get(
    tags=["Ideas"],
    summary="Get all ideas",
    description="Retrieve all ideas for the authenticated user with optional search and category filtering. Supports pagination."
)
async def get_ideas(
    request: Request,
    search: Optional[str] = Query(default=None, description="Optional search term to filter ideas by title"),
    category: Optional[UUID] = Query(default=None, description="Optional category ID to filter ideas"),
    page: int = Query(default=1, description="Page number for pagination (default: 1)"),
    limit: int = Query(default=20, description="Number of ideas per page (default: 20, max: 100)")
) -> IdeasResponse:
    """
    Retrieve all ideas for the authenticated user with optional filtering and pagination.
    
    This endpoint returns ideas with optional search and category filtering.
    Results are paginated and ordered by creation date (newest first).
    
    Args:
        search: Optional search term to filter ideas by title
        category: Optional category ID to filter ideas
        page: Page number for pagination (default: 1)
        limit: Number of ideas per page (default: 20, max: 100)
        
    Returns:
        IdeasResponse: Array of ideas with pagination metadata
        
    Raises:
        400: Bad request - Invalid pagination parameters
        401: Authentication required - Include valid Authorization header
        429: Rate limit exceeded - Too many requests, retry after delay
    """
    # Validate pagination parameters
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be greater than 0")
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")
    
    user_id = await get_current_user_id(request)
    result = await idea_service.get_all_ideas(
        user_id=user_id,
        search=search,
        category=category,
        page=page,
        limit=limit
    )
    
    try:
        ideas_response = [IdeaResponse.model_validate_from_orm(idea) for idea in result["ideas"]]
    except Exception as e:
        print(f"[DEBUG] Error converting ideas to IdeaResponse: {e}")
        raise
    return IdeasResponse(
        ideas=ideas_response,
        meta=PaginationMeta(
            total=result["total"],
            page=result["page"],
            limit=result["limit"],
            pages=result["pages"]
        )
    )


@post(
    tags=["Ideas"],
    summary="Create a new idea",
    description="Create a new idea for the authenticated user with title, description, category, and optional tags."
)
async def create_idea(request: Request, data: IdeaCreate) -> IdeaResponse:
    """
    Create a new idea for the authenticated user.
    
    This endpoint creates a new idea with the specified properties.
    The category must exist in the system.
    
    Args:
        data: IdeaCreate schema containing idea details
        
    Returns:
        IdeaResponse: The created idea with generated ID and timestamps
        
    Raises:
        400: Bad request - Invalid request format or missing required fields
        401: Authentication required - Include valid Authorization header
        404: Category not found - Category with specified ID does not exist
        422: Validation error - Required fields missing or invalid values
        429: Rate limit exceeded - Too many requests, retry after delay
    """
    try:
        user_id = await get_current_user_id(request)
        idea = await idea_service.create_idea(data, user_id)
        return IdeaResponse.model_validate_from_orm(idea)
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Category not found")


@get(
    tags=["Ideas"],
    summary="Get a specific idea",
    description="Retrieve a specific idea by its ID for the authenticated user."
)
async def get_idea(request: Request, idea_id: UUID) -> IdeaResponse:
    """
    Retrieve a specific idea by ID for the authenticated user.
    
    This endpoint returns the complete details of a specific idea.
    
    Args:
        idea_id: UUID of the idea to retrieve
        
    Returns:
        IdeaResponse: The idea with complete details
        
    Raises:
        400: Bad request - Invalid UUID format
        401: Authentication required - Include valid Authorization header
        404: Idea not found - Idea with specified ID does not exist
        429: Rate limit exceeded - Too many requests, retry after delay
    """
    try:
        user_id = await get_current_user_id(request)
        idea = await idea_service.get_idea_by_id(idea_id, user_id)
        return IdeaResponse.model_validate_from_orm(idea)
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Idea not found")


@put(
    tags=["Ideas"],
    summary="Update an idea",
    description="Update an existing idea's properties for the authenticated user. Only provided fields will be updated."
)
async def update_idea(request: Request, idea_id: UUID, data: IdeaUpdate) -> IdeaResponse:
    """
    Update an existing idea's properties for the authenticated user.
    
    This endpoint allows partial updates to an idea. Only the fields provided
    in the request will be updated.
    
    Args:
        idea_id: UUID of the idea to update
        data: IdeaUpdate schema containing fields to update
        
    Returns:
        IdeaResponse: The updated idea with new timestamps
        
    Raises:
        400: Bad request - Invalid request format or missing required fields
        401: Authentication required - Include valid Authorization header
        404: Idea or category not found - Idea or category with specified ID does not exist
        422: Validation error - Provided fields contain invalid values
        429: Rate limit exceeded - Too many requests, retry after delay
    """
    try:
        user_id = await get_current_user_id(request)
        idea = await idea_service.update_idea(idea_id, data, user_id)
        return IdeaResponse.model_validate_from_orm(idea)
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Idea not found")


@delete(
    status_code=200,
    tags=["Ideas"],
    summary="Delete an idea",
    description="Delete a specific idea by its ID for the authenticated user. This action cannot be undone."
)
async def delete_idea(request: Request, idea_id: UUID) -> dict:
    """
    Delete a specific idea for the authenticated user.
    
    This endpoint permanently deletes an idea. This action cannot be undone.
    
    Args:
        idea_id: UUID of the idea to delete
        
    Returns:
        dict: Success message confirming deletion
        
    Raises:
        400: Bad request - Invalid UUID format
        401: Authentication required - Include valid Authorization header
        404: Idea not found - Idea with specified ID does not exist
        429: Rate limit exceeded - Too many requests, retry after delay
    """
    try:
        user_id = await get_current_user_id(request)
        await idea_service.delete_idea(idea_id, user_id)
        return {"message": "Idea deleted successfully"}
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Idea not found") 