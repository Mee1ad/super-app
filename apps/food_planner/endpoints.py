from datetime import date
from typing import Optional
from uuid import UUID
from esmerald import get, post, put, delete, HTTPException, status, Query, UploadFile, File
from esmerald.exceptions import NotFound
from edgy.exceptions import ObjectNotFound
from .models import MealType, FoodEntry
from .schemas import (
    MealTypeCreate, MealTypeResponse, MealTypesResponse,
    FoodEntryCreate, FoodEntryUpdate, FoodEntryResponse, FoodEntriesResponse,
    FoodSummaryResponse, CalendarResponse
)
from .services import MealTypeService, FoodEntryService
from db.session import database

meal_type_service = MealTypeService(database)
food_entry_service = FoodEntryService(database)

@get(
    path="/api/meal-types",
    tags=["Meal Types"],
    summary="Get all meal types",
    description="Retrieve all available meal types (breakfast, lunch, dinner, snack)."
)
async def get_meal_types() -> MealTypesResponse:
    meal_types = await meal_type_service.get_all_meal_types()
    return MealTypesResponse(meal_types=[MealTypeResponse.model_validate(meal_type) for meal_type in meal_types])

@get(
    path="/api/food-entries",
    tags=["Food Planner"],
    summary="Get all food entries",
    description="Retrieve all food entries with optional search, filtering, and pagination."
)
async def get_food_entries(
    search: Optional[str] = Query(default=None, description="Optional search term to filter entries by name"),
    category: Optional[str] = Query(default=None, description="Filter by category: 'planned' or 'eaten'"),
    meal_type: Optional[str] = Query(default=None, description="Filter by meal type ID"),
    date_filter: Optional[date] = Query(default=None, description="Filter by specific date"),
    page: int = Query(default=1, description="Page number for pagination (default: 1)"),
    limit: int = Query(default=20, description="Number of entries per page (default: 20, max: 100)")
) -> FoodEntriesResponse:
    result = await food_entry_service.get_all_entries(
        search=search, 
        category=category, 
        meal_type=meal_type, 
        date_filter=date_filter, 
        page=page, 
        limit=limit
    )
    return FoodEntriesResponse(
        entries=[FoodEntryResponse.model_validate_from_orm(entry) for entry in result["entries"]],
        meta={
            "total": result["total"],
            "page": result["page"],
            "limit": result["limit"],
            "pages": result["pages"]
        }
    )

@post(
    path="/api/food-entries",
    tags=["Food Planner"],
    summary="Create a new food entry",
    description="Create a new food entry with name, category, meal type, time, and optional details."
)
async def create_food_entry(data: FoodEntryCreate) -> FoodEntryResponse:
    try:
        entry = await food_entry_service.create_entry(data)
        return FoodEntryResponse.model_validate_from_orm(entry)
    except ObjectNotFound:
        raise NotFound("Meal type not found")

@get(
    path="/api/food-entries/{entry_id:uuid}",
    tags=["Food Planner"],
    summary="Get a specific food entry",
    description="Retrieve a specific food entry by its ID."
)
async def get_food_entry(entry_id: UUID) -> FoodEntryResponse:
    try:
        entry = await food_entry_service.get_entry_by_id(entry_id)
        return FoodEntryResponse.model_validate_from_orm(entry)
    except ObjectNotFound:
        raise NotFound("Food entry not found")

@put(
    path="/api/food-entries/{entry_id:uuid}",
    tags=["Food Planner"],
    summary="Update a food entry",
    description="Update an existing food entry's properties. Only provided fields will be updated."
)
async def update_food_entry(entry_id: UUID, data: FoodEntryUpdate) -> FoodEntryResponse:
    try:
        entry = await food_entry_service.update_entry(entry_id, data)
        return FoodEntryResponse.model_validate_from_orm(entry)
    except ObjectNotFound:
        raise NotFound("Food entry or meal type not found")

@delete(
    path="/api/food-entries/{entry_id:uuid}",
    status_code=200,
    tags=["Food Planner"],
    summary="Delete a food entry",
    description="Delete a specific food entry by its ID. This action cannot be undone."
)
async def delete_food_entry(entry_id: UUID) -> dict:
    try:
        await food_entry_service.delete_entry(entry_id)
        return {"message": "Food entry deleted successfully"}
    except ObjectNotFound:
        raise NotFound("Food entry not found")

@get(
    path="/api/food-entries/summary",
    tags=["Food Planner"],
    summary="Get food entries summary",
    description="Get summary statistics for food entries within a date range."
)
async def get_food_summary(
    start_date: Optional[date] = Query(default=None, description="Start date for summary (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(default=None, description="End date for summary (YYYY-MM-DD)")
) -> FoodSummaryResponse:
    summary = await food_entry_service.get_summary(start_date=start_date, end_date=end_date)
    return FoodSummaryResponse(**summary)

@get(
    path="/api/food-entries/calendar",
    tags=["Food Planner"],
    summary="Get calendar data",
    description="Get daily summaries for calendar view within a date range."
)
async def get_calendar_data(
    start_date: Optional[date] = Query(default=None, description="Start date for calendar (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(default=None, description="End date for calendar (YYYY-MM-DD)")
) -> CalendarResponse:
    calendar_data = await food_entry_service.get_calendar_data(start_date=start_date, end_date=end_date)
    return CalendarResponse(days=calendar_data)

@post(
    path="/api/upload-food-image",
    tags=["Food Planner"],
    summary="Upload a food image",
    description="Upload an image for food entries and return its URL."
)
async def upload_food_image(file: UploadFile = File(...)) -> dict:
    # Stub: In production, save file and return URL
    return {"url": f"/static/uploads/food/{file.filename}"} 