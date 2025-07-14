from typing import List as ListType, Optional
from uuid import UUID
from edgy import Database
from edgy.exceptions import ObjectNotFound
from .models import Mood, DiaryEntry
from .schemas import MoodCreate, DiaryEntryCreate, DiaryEntryUpdate

class MoodService:
    def __init__(self, database: Database):
        self.database = database

    async def get_all_moods(self) -> ListType[Mood]:
        return await Mood.query.all().order_by("name")

    async def create_mood(self, mood_data: MoodCreate) -> Mood:
        return await Mood.query.create(**mood_data.model_dump())

class DiaryService:
    def __init__(self, database: Database):
        self.database = database

    async def get_all_entries(self, user_id: UUID, search: Optional[str] = None, mood: Optional[str] = None, page: int = 1, limit: int = 20) -> dict:
        query = DiaryEntry.query.filter(user_id=user_id)
        if search:
            query = query.filter(title__icontains=search)
        if mood:
            query = query.filter(mood=mood)
        total = await query.count()
        offset = (page - 1) * limit
        entries = await query.offset(offset).limit(limit).order_by("-created_at")
        return {
            "entries": entries,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }

    async def get_entry_by_id(self, entry_id: UUID, user_id: UUID) -> DiaryEntry:
        entry = await DiaryEntry.query.filter(id=entry_id, user_id=user_id).first()
        if not entry:
            raise ObjectNotFound("Diary entry not found")
        return entry

    async def create_entry(self, entry_data: DiaryEntryCreate, user_id: UUID) -> DiaryEntry:
        await Mood.query.get(id=entry_data.mood)
        entry_data_dict = entry_data.model_dump()
        entry_data_dict['user_id'] = user_id
        return await DiaryEntry.query.create(**entry_data_dict)

    async def update_entry(self, entry_id: UUID, entry_data: DiaryEntryUpdate, user_id: UUID) -> DiaryEntry:
        entry = await self.get_entry_by_id(entry_id, user_id)
        update_data = {k: v for k, v in entry_data.model_dump().items() if v is not None}
        if 'mood' in update_data:
            await Mood.query.get(id=update_data['mood'])
        await entry.update(**update_data)
        # Reload the entry to ensure user relation is loaded
        return await self.get_entry_by_id(entry_id, user_id)

    async def delete_entry(self, entry_id: UUID, user_id: UUID) -> bool:
        entry = await self.get_entry_by_id(entry_id, user_id)
        await entry.delete()
        return True 