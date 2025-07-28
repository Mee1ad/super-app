from datetime import datetime
from typing import Optional, List
from uuid import UUID
from esmerald import get, post, put, delete, HTTPException, status, Query, Request, File, UploadFile
import os
import uuid
from pathlib import Path
from apps.food_tracker.models import FoodEntry
from apps.food_tracker.schemas import (
    FoodEntryCreate, FoodEntryUpdate, FoodEntryResponse,
    FoodEntriesResponse, FoodSummaryResponse
)
from apps.food_tracker.services import FoodTrackerService
from core.dependencies import get_current_user_dependency
from core.exceptions import NotFoundError, ValidationError


UPLOAD_DIR = Path("uploads/food_images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

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
    except HTTPException:
        # Re-raise HTTP exceptions as they are expected
        raise
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
    entry_id: UUID
) -> FoodEntryResponse:
    """Get a specific food entry by ID"""
    try:
        current_user = await get_current_user_dependency(request)
        service = FoodTrackerService(current_user.id)
        entry = await service.get_food_entry(str(entry_id))
        return entry
    except HTTPException:
        # Re-raise HTTP exceptions as they are expected
        raise
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
    except HTTPException:
        # Re-raise HTTP exceptions as they are expected
        raise
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
    entry_id: UUID,
    data: FoodEntryUpdate
) -> FoodEntryResponse:
    """Update an existing food entry"""
    try:
        current_user = await get_current_user_dependency(request)
        service = FoodTrackerService(current_user.id)
        entry = await service.update_food_entry(str(entry_id), data)
        return entry
    except HTTPException:
        # Re-raise HTTP exceptions as they are expected
        raise
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
    entry_id: UUID
) -> dict:
    """Delete a food entry"""
    try:
        current_user = await get_current_user_dependency(request)
        service = FoodTrackerService(current_user.id)
        await service.delete_food_entry(str(entry_id))
        return {"message": "Food entry deleted successfully"}
    except HTTPException:
        # Re-raise HTTP exceptions as they are expected
        raise
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
    except HTTPException:
        # Re-raise HTTP exceptions as they are expected
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve food summary: {str(e)}"
        ) 


@post(
    tags=["Food Tracker"],
    summary="Upload food image",
    description="Upload an image for food entries and return its URL"
)
async def upload_food_image(file: UploadFile = File(...)) -> dict:
    """Upload a food image and return its URL"""
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only image files are allowed"
            )
        # Validate file size (5MB limit)
        content = await file.read()
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large. Maximum size is 5MB"
            )
        # Generate unique filename
        file_extension = Path(file.filename).suffix or ".jpg"
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        # Save file
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        # Return URL
        return {"url": f"/static/food_images/{unique_filename}"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        ) 