from datetime import datetime
from typing import Optional
from esmerald import get, post, put, delete, HTTPException, status, Query, Request
from apps.food_tracker.models import FoodEntry
from apps.food_tracker.schemas import (
    FoodEntryCreate, FoodEntryUpdate, FoodEntryResponse,
    FoodEntriesResponse, FoodSummaryResponse
)
from apps.food_tracker.services import FoodTrackerService
from core.dependencies import get_current_user_dependency
from core.exceptions import NotFoundError, ValidationError


@get(
    tags=["Food Tracker"],
    summary="Get food entries",
    description="Get food entries with filtering and pagination"
)
async def get_food_entries(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term for food names"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter")
) -> FoodEntriesResponse:
    """Get food entries with filtering and pagination"""
    try:
        current_user = await get_current_user_dependency(request)
        service = FoodTrackerService(current_user.id)
        result = await service.get_food_entries(
            page=page,
            limit=limit,
            search=search,
            start_date=start_date,
            end_date=end_date,
            min_price=min_price,
            max_price=max_price
        )
        
        return FoodEntriesResponse(
            entries=result["entries"],
            total=result["total"],
            page=result["page"],
            limit=result["limit"],
            pages=result["pages"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve food entries: {str(e)}"
        )


@get(
    tags=["Food Tracker"],
    summary="Get a specific food entry",
    description="Get a specific food entry by ID"
)
async def get_food_entry(
    request: Request,
    entry_id: str
) -> FoodEntryResponse:
    """Get a specific food entry by ID"""
    try:
        current_user = await get_current_user_dependency(request)
        service = FoodTrackerService(current_user.id)
        entry = await service.get_food_entry(entry_id)
        return entry
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve food entry: {str(e)}"
        )


@post(
    tags=["Food Tracker"],
    summary="Create a new food entry",
    description="Create a new food entry",
    status_code=201
)
async def create_food_entry(
    request: Request,
    data: FoodEntryCreate
) -> FoodEntryResponse:
    """Create a new food entry"""
    try:
        current_user = await get_current_user_dependency(request)
        service = FoodTrackerService(current_user.id)
        entry = await service.create_food_entry(data)
        return entry
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create food entry: {str(e)}"
        )


@put(
    tags=["Food Tracker"],
    summary="Update a food entry",
    description="Update an existing food entry"
)
async def update_food_entry(
    request: Request,
    entry_id: str,
    data: FoodEntryUpdate
) -> FoodEntryResponse:
    """Update an existing food entry"""
    try:
        current_user = await get_current_user_dependency(request)
        service = FoodTrackerService(current_user.id)
        entry = await service.update_food_entry(entry_id, data)
        return entry
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update food entry: {str(e)}"
        )


@delete(
    tags=["Food Tracker"],
    summary="Delete a food entry",
    description="Delete a food entry",
    status_code=200
)
async def delete_food_entry(
    request: Request,
    entry_id: str
) -> dict:
    """Delete a food entry"""
    try:
        current_user = await get_current_user_dependency(request)
        service = FoodTrackerService(current_user.id)
        await service.delete_food_entry(entry_id)
        return {"message": "Food entry deleted successfully"}
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete food entry: {str(e)}"
        )


@get(
    tags=["Food Tracker"],
    summary="Get food summary",
    description="Get food summary statistics"
)
async def get_food_summary(
    request: Request,
    start_date: Optional[datetime] = Query(None, description="Start date for summary"),
    end_date: Optional[datetime] = Query(None, description="End date for summary")
) -> FoodSummaryResponse:
    """Get food summary statistics"""
    try:
        current_user = await get_current_user_dependency(request)
        service = FoodTrackerService(current_user.id)
        summary = await service.get_food_summary(start_date, end_date)
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve food summary: {str(e)}"
        ) 