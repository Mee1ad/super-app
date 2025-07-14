from typing import List as ListType, Optional
from uuid import UUID
from esmerald import get, post, put, delete, HTTPException, status, Query, UploadFile, File, Request
from esmerald.exceptions import NotFound
from edgy.exceptions import ObjectNotFound
from .models import Mood, DiaryEntry
from .schemas import (
    MoodCreate, MoodResponse, MoodsResponse,
    DiaryEntryCreate, DiaryEntryUpdate, DiaryEntryResponse, DiaryEntriesResponse
)
from .services import MoodService, DiaryService
from db.session import database
from core.dependencies import get_current_user_id

mood_service = MoodService(database)
diary_service = DiaryService(database)

@get(
    path="/api/moods",
    tags=["Moods"],
    summary="Get all moods",
    description="Retrieve all available moods."
)
async def get_moods() -> MoodsResponse:
    moods = await mood_service.get_all_moods()
    return MoodsResponse(moods=[MoodResponse.model_validate(mood) for mood in moods])

@get(
    path="/api/diary-entries",
    tags=["Diary"],
    summary="Get all diary entries",
    description="Retrieve all diary entries for the authenticated user with optional search and mood filtering. Supports pagination."
)
async def get_diary_entries(
    request: Request,
    search: Optional[str] = Query(default=None, description="Optional search term to filter entries by title"),
    mood: Optional[str] = Query(default=None, description="Optional mood ID to filter entries"),
    page: int = Query(default=1, description="Page number for pagination (default: 1)"),
    limit: int = Query(default=20, description="Number of entries per page (default: 20, max: 100)")
) -> DiaryEntriesResponse:
    user_id = await get_current_user_id(request)
    result = await diary_service.get_all_entries(user_id=user_id, search=search, mood=mood, page=page, limit=limit)
    return DiaryEntriesResponse(
        entries=[DiaryEntryResponse.model_validate_from_orm(entry) for entry in result["entries"]],
        meta={
            "total": result["total"],
            "page": result["page"],
            "limit": result["limit"],
            "pages": result["pages"]
        }
    )

@post(
    path="/api/diary-entries",
    tags=["Diary"],
    summary="Create a new diary entry",
    description="Create a new diary entry for the authenticated user with title, content, mood, and optional images."
)
async def create_diary_entry(request: Request, data: DiaryEntryCreate) -> DiaryEntryResponse:
    try:
        user_id = await get_current_user_id(request)
        entry = await diary_service.create_entry(data, user_id)
        return DiaryEntryResponse.model_validate_from_orm(entry)
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Mood not found")

@get(
    path="/api/diary-entries/{entry_id:uuid}",
    tags=["Diary"],
    summary="Get a specific diary entry",
    description="Retrieve a specific diary entry by its ID for the authenticated user."
)
async def get_diary_entry(request: Request, entry_id: UUID) -> DiaryEntryResponse:
    try:
        user_id = await get_current_user_id(request)
        entry = await diary_service.get_entry_by_id(entry_id, user_id)
        return DiaryEntryResponse.model_validate_from_orm(entry)
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Diary entry not found")

@put(
    path="/api/diary-entries/{entry_id:uuid}",
    tags=["Diary"],
    summary="Update a diary entry",
    description="Update an existing diary entry's properties for the authenticated user. Only provided fields will be updated."
)
async def update_diary_entry(request: Request, entry_id: UUID, data: DiaryEntryUpdate) -> DiaryEntryResponse:
    try:
        user_id = await get_current_user_id(request)
        entry = await diary_service.update_entry(entry_id, data, user_id)
        return DiaryEntryResponse.model_validate_from_orm(entry)
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Diary entry or mood not found")

@delete(
    path="/api/diary-entries/{entry_id:uuid}",
    status_code=200,
    tags=["Diary"],
    summary="Delete a diary entry",
    description="Delete a specific diary entry by its ID for the authenticated user. This action cannot be undone."
)
async def delete_diary_entry(request: Request, entry_id: UUID) -> dict:
    try:
        user_id = await get_current_user_id(request)
        await diary_service.delete_entry(entry_id, user_id)
        return {"message": "Diary entry deleted successfully"}
    except ObjectNotFound:
        raise HTTPException(status_code=404, detail="Diary entry not found")

@post(
    path="/api/upload-image",
    tags=["Diary"],
    summary="Upload an image",
    description="Upload an image and return its URL. (Stub implementation)"
)
async def upload_image(file: UploadFile = File(...)) -> dict:
    # Stub: In production, save file and return URL
    return {"url": f"/static/uploads/{file.filename}"} 