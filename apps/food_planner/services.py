from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
from edgy import Database
from edgy.exceptions import ObjectNotFound
from .models import MealType, FoodEntry
from .schemas import MealTypeCreate, FoodEntryCreate, FoodEntryUpdate

class MealTypeService:
    def __init__(self, database: Database):
        self.database = database

    async def get_all_meal_types(self) -> List[MealType]:
        return await MealType.query.all().order_by("name")

    async def get_meal_type_by_id(self, meal_type_id: str) -> MealType:
        meal_type = await MealType.query.get(id=meal_type_id)
        if not meal_type:
            raise ObjectNotFound("Meal type not found")
        return meal_type

    async def create_meal_type(self, meal_type_data: MealTypeCreate) -> MealType:
        return await MealType.query.create(**meal_type_data.model_dump())

class FoodEntryService:
    def __init__(self, database: Database):
        self.database = database

    async def get_all_entries(
        self, 
        user_id: UUID,
        search: Optional[str] = None,
        category: Optional[str] = None,
        meal_type: Optional[str] = None,
        date_filter: Optional[date] = None,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        query = FoodEntry.query.filter(user_id=user_id)
        
        # Apply filters
        if search:
            query = query.filter(name__icontains=search)
        if category:
            query = query.filter(category=category)
        if meal_type:
            query = query.filter(meal_type_id=meal_type)
        if date_filter:
            query = query.filter(date=date_filter)
        
        # Get total count
        total = await query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        entries = await query.offset(offset).limit(limit).all()
        
        # Calculate pagination info
        pages = (total + limit - 1) // limit if total > 0 else 0
        
        return {
            "entries": entries,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages
        }

    async def get_entry_by_id(self, entry_id: UUID, user_id: UUID) -> FoodEntry:
        entry = await FoodEntry.query.filter(id=entry_id, user_id=user_id).first()
        if not entry:
            raise ObjectNotFound("Food entry not found")
        return entry

    async def create_entry(self, entry_data: FoodEntryCreate, user_id: UUID) -> FoodEntry:
        entry_dict = entry_data.model_dump()
        entry_dict['user_id'] = user_id
        return await FoodEntry.query.create(**entry_dict)

    async def update_entry(self, entry_id: UUID, entry_data: FoodEntryUpdate, user_id: UUID) -> FoodEntry:
        entry = await self.get_entry_by_id(entry_id, user_id)
        
        # Only include non-None values
        update_data = {k: v for k, v in entry_data.model_dump().items() if v is not None}
        
        if update_data:
            await entry.update(**update_data)
            await entry.save()
        
        # Reload the entry to ensure user relation is loaded
        return await self.get_entry_by_id(entry_id, user_id)

    async def delete_entry(self, entry_id: UUID, user_id: UUID) -> None:
        entry = await self.get_entry_by_id(entry_id, user_id)
        await entry.delete()

    async def get_summary(self, user_id: UUID, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict[str, int]:
        query = FoodEntry.query.filter(user_id=user_id)
        
        if start_date:
            query = query.filter(date__gte=start_date)
        if end_date:
            query = query.filter(date__lte=end_date)
        
        entries = await query.all()
        
        planned_count = sum(1 for entry in entries if entry.category == "planned")
        eaten_count = sum(1 for entry in entries if entry.category == "eaten")
        followed_plan_count = sum(1 for entry in entries if entry.category == "eaten" and entry.followed_plan)
        off_plan_count = eaten_count - followed_plan_count
        
        return {
            "planned_count": planned_count,
            "eaten_count": eaten_count,
            "followed_plan_count": followed_plan_count,
            "off_plan_count": off_plan_count
        }

    async def get_calendar_data(self, user_id: UUID, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today() + timedelta(days=30)
        
        query = FoodEntry.query.filter(user_id=user_id, date__gte=start_date, date__lte=end_date)
        entries = await query.all()
        
        # Group entries by date
        entries_by_date = {}
        for entry in entries:
            if entry.date not in entries_by_date:
                entries_by_date[entry.date] = []
            entries_by_date[entry.date].append(entry)
        
        # Create day summaries
        calendar_data = []
        current_date = start_date
        while current_date <= end_date:
            day_entries = entries_by_date.get(current_date, [])
            planned_count = sum(1 for entry in day_entries if entry.category == "planned")
            eaten_count = sum(1 for entry in day_entries if entry.category == "eaten")
            followed_plan = any(entry.category == "eaten" and entry.followed_plan for entry in day_entries)
            
            calendar_data.append({
                "date": current_date,
                "planned_count": planned_count,
                "eaten_count": eaten_count,
                "followed_plan": followed_plan
            })
            
            current_date += timedelta(days=1)
        
        return calendar_data

from db.session import database

meal_type_service = MealTypeService(database)
food_entry_service = FoodEntryService(database) 