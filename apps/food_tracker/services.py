from datetime import datetime, timedelta
from typing import Optional, List, Dict
from edgy import QuerySet
from apps.food_tracker.models import FoodEntry
from apps.food_tracker.schemas import FoodEntryCreate, FoodEntryUpdate, FoodSummaryResponse
from core.exceptions import NotFoundError, ValidationError


class FoodTrackerService:
    """Service for food tracker operations"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
    
    async def get_food_entries(
        self,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> Dict:
        """Get food entries with filtering and pagination"""
        query = FoodEntry.query.filter(user_id=self.user_id)
        
        # Apply search filter
        if search:
            query = query.filter(name__icontains=search)
        
        # Apply date range filter
        if start_date:
            query = query.filter(date__gte=start_date)
        if end_date:
            query = query.filter(date__lte=end_date)
        
        # Apply price range filter
        if min_price is not None:
            query = query.filter(price__gte=min_price)
        if max_price is not None:
            query = query.filter(price__lte=max_price)
        
        # Get total count
        total = await query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        entries = await query.offset(offset).limit(limit).all()
        
        # Calculate pagination info
        pages = (total + limit - 1) // limit
        
        return {
            "entries": entries,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages
        }
    
    async def get_food_entry(self, entry_id: str) -> FoodEntry:
        """Get a specific food entry by ID"""
        entry = await FoodEntry.query.filter(
            id=entry_id,
            user_id=self.user_id
        ).first()
        
        if not entry:
            raise NotFoundError(f"Food entry with ID {entry_id} not found")
        
        return entry
    
    async def create_food_entry(self, data: FoodEntryCreate) -> FoodEntry:
        """Create a new food entry"""
        entry_data = data.dict()
        entry_data["user_id"] = self.user_id
        
        # Validate price if provided
        if entry_data.get("price") is not None and entry_data["price"] < 0:
            raise ValidationError("Price cannot be negative")
        
        entry = await FoodEntry.query.create(**entry_data)
        return entry
    
    async def update_food_entry(self, entry_id: str, data: FoodEntryUpdate) -> FoodEntry:
        """Update an existing food entry"""
        entry = await self.get_food_entry(entry_id)
        
        update_data = data.dict(exclude_unset=True)
        
        # Validate price if provided
        if "price" in update_data and update_data["price"] is not None:
            if update_data["price"] < 0:
                raise ValidationError("Price cannot be negative")
        
        # Update the entry
        await entry.update(**update_data)
        await entry.save()
        
        return entry
    
    async def delete_food_entry(self, entry_id: str) -> bool:
        """Delete a food entry"""
        entry = await self.get_food_entry(entry_id)
        await entry.delete()
        return True
    
    async def get_food_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> FoodSummaryResponse:
        """Get food summary statistics"""
        query = FoodEntry.query.filter(user_id=self.user_id)
        
        # Apply date range filter
        if start_date:
            query = query.filter(date__gte=start_date)
        if end_date:
            query = query.filter(date__lte=end_date)
        
        entries = await query.all()
        
        # Calculate statistics
        total_entries = len(entries)
        total_spent = sum(entry.price or 0 for entry in entries)
        average_price = total_spent / total_entries if total_entries > 0 else 0
        
        # Group entries by date
        entries_by_date: Dict[str, int] = {}
        for entry in entries:
            date_str = entry.date.strftime("%Y-%m-%d")
            entries_by_date[date_str] = entries_by_date.get(date_str, 0) + 1
        
        return FoodSummaryResponse(
            total_entries=total_entries,
            total_spent=total_spent,
            average_price=average_price,
            entries_by_date=entries_by_date
        ) 