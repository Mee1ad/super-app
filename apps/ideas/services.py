# services for ideas app 
from typing import List as ListType, Optional
from uuid import UUID

from edgy import Database
from edgy.exceptions import ObjectNotFound

from .models import Category, Idea
from .schemas import (
    CategoryCreate, CategoryUpdate, IdeaCreate, IdeaUpdate
)


class CategoryService:
    """Service for category operations"""
    
    def __init__(self, database: Database):
        self.database = database
    
    async def get_all_categories(self) -> ListType[Category]:
        """Get all categories ordered by name"""
        return await Category.query.all().order_by("name")
    
    async def get_category_by_id(self, category_id: str) -> Category:
        """Get a category by ID"""
        category = await Category.query.get(id=category_id)
        if not category:
            raise ObjectNotFound("Category not found")
        return category
    
    async def create_category(self, category_data: CategoryCreate) -> Category:
        """Create a new category"""
        return await Category.query.create(**category_data.model_dump())
    
    async def update_category(self, category_id: str, category_data: CategoryUpdate) -> Category:
        """Update a category"""
        category = await self.get_category_by_id(category_id)
        update_data = {k: v for k, v in category_data.model_dump().items() if v is not None}
        return await category.update(**update_data)
    
    async def delete_category(self, category_id: str) -> bool:
        """Delete a category"""
        category = await self.get_category_by_id(category_id)
        await category.delete()
        return True


class IdeaService:
    """Service for idea operations"""
    
    def __init__(self, database: Database):
        self.database = database
    
    async def get_all_ideas(
        self, 
        user_id: UUID,
        search: Optional[str] = None, 
        category: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> dict:
        """Get all ideas for a specific user with optional filtering and pagination"""
        query = Idea.query.filter(user_id=user_id)
        
        # Apply search filter
        if search:
            query = query.filter(title__icontains=search)
        
        # Apply category filter
        if category:
            query = query.filter(category=category)
        
        # Get total count for pagination
        total = await query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        ideas = await query.offset(offset).limit(limit).order_by("-created_at")
        
        return {
            "ideas": ideas,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    
    async def get_idea_by_id(self, idea_id: UUID, user_id: UUID) -> Idea:
        """Get an idea by ID for a specific user"""
        idea = await Idea.query.filter(id=idea_id, user_id=user_id).first()
        if not idea:
            raise ObjectNotFound("Idea not found")
        return idea
    
    async def create_idea(self, idea_data: IdeaCreate, user_id: UUID) -> Idea:
        """Create a new idea for a specific user"""
        # Validate that the category exists
        await Category.query.get(id=idea_data.category)
        
        idea_data_dict = idea_data.model_dump()
        idea_data_dict['user_id'] = user_id
        return await Idea.query.create(**idea_data_dict)
    
    async def update_idea(self, idea_id: UUID, idea_data: IdeaUpdate, user_id: UUID) -> Idea:
        """Update an idea for a specific user"""
        idea = await self.get_idea_by_id(idea_id, user_id)
        update_data = {k: v for k, v in idea_data.model_dump().items() if v is not None}
        
        # Validate category if it's being updated
        if 'category' in update_data:
            await Category.query.get(id=update_data['category'])
        
        await idea.update(**update_data)
        # Reload the idea to ensure user relation is loaded
        return await self.get_idea_by_id(idea_id, user_id)
    
    async def delete_idea(self, idea_id: UUID, user_id: UUID) -> bool:
        """Delete an idea for a specific user"""
        idea = await self.get_idea_by_id(idea_id, user_id)
        await idea.delete()
        return True 