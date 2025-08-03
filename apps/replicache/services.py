import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from uuid import uuid4

from apps.todo.models import List as TodoList, Task, ShoppingItem
from apps.food_tracker.models import FoodEntry
from apps.diary.models import DiaryEntry
from apps.ideas.models import Idea

logger = logging.getLogger(__name__)

# Todo Context Handlers
async def process_todo_mutation(mutation: Dict[str, Any], user_id: str) -> None:
    """Process todo mutations for todo-replicache-flat client"""
    mutation_name = mutation.get('name', '')
    args = mutation.get('args', {})
    
    try:
        if mutation_name == 'createItem':
            # Create new todo item
            item_id = args.get('id', str(uuid4()))
            list_id = args.get('listId')
            title = args.get('title', '')
            completed = args.get('completed', False)
            order = args.get('order', 0)
            
            # Determine if it's a task or shopping item based on list type
            try:
                list_obj = await TodoList.query.get(id=list_id, user_id=user_id)
            except Exception as e:
                logger.error(f"List not found: {list_id} for user {user_id}, error: {e}")
                # Default to task type if list is not found
                list_obj = type('obj', (object,), {'type': 'task'})()
            
            if list_obj.type == 'task':
                await Task.query.create(
                    id=item_id,
                    user_id=user_id,
                    list=list_id,
                    title=title,
                    checked=completed,
                    position=order
                )
            else:  # shopping
                await ShoppingItem.query.create(
                    id=item_id,
                    user_id=user_id,
                    list=list_id,
                    title=title,
                    checked=completed,
                    position=order
                )
                
        elif mutation_name == 'updateItem':
            # Update existing todo item
            item_id = args.get('id')
            updates = {}
            
            if 'title' in args:
                updates['title'] = args['title']
            if 'completed' in args:
                updates['checked'] = args['completed']
            if 'order' in args:
                updates['position'] = args['order']
            
            # Try to update as task first, then shopping item
            try:
                await Task.query.filter(id=item_id, user_id=user_id).update(**updates)
            except:
                await ShoppingItem.query.filter(id=item_id, user_id=user_id).update(**updates)
                
        elif mutation_name == 'deleteItem':
            # Delete todo item
            item_id = args.get('id')
            
            # Try to delete as task first, then shopping item
            try:
                await Task.query.filter(id=item_id, user_id=user_id).delete()
            except:
                await ShoppingItem.query.filter(id=item_id, user_id=user_id).delete()
                
    except Exception as e:
        logger.error(f"Error processing todo mutation {mutation_name}: {e}")
        raise

async def get_todo_patch(user_id: str) -> List[Dict[str, Any]]:
    """Get todo data for todo-replicache-flat client"""
    try:
        patch = []
        
        # Get all lists
        lists = await TodoList.query.filter(user_id=user_id).all()
        for list_obj in lists:
            patch.append({
                "op": "put",
                "key": f"list/{list_obj.id}",
                "value": {
                    "id": str(list_obj.id),
                    "type": list_obj.type,
                    "title": list_obj.title,
                    "variant": list_obj.variant
                }
            })
        
        # Get all tasks
        tasks = await Task.query.filter(user_id=user_id).all()
        for task in tasks:
            patch.append({
                "op": "put",
                "key": f"task/{task.id}",
                "value": {
                    "id": str(task.id),
                    "listId": str(task.list_id),
                    "title": task.title,
                    "description": task.description,
                    "completed": task.checked,
                    "order": task.position,
                    "variant": task.variant
                }
            })
        
        # Get all shopping items
        items = await ShoppingItem.query.filter(user_id=user_id).all()
        for item in items:
            patch.append({
                "op": "put",
                "key": f"item/{item.id}",
                "value": {
                    "id": str(item.id),
                    "listId": str(item.list_id),
                    "title": item.title,
                    "url": item.url,
                    "price": item.price,
                    "source": item.source,
                    "completed": item.checked,
                    "order": item.position,
                    "variant": item.variant
                }
            })
        
        return patch
        
    except Exception as e:
        logger.error(f"Error getting todo patch: {e}")
        return []

# Food Tracker Context Handlers
async def process_food_mutation(mutation: Dict[str, Any], user_id: str) -> None:
    """Process food mutations for food-tracker-replicache client"""
    mutation_name = mutation.get('name', '')
    args = mutation.get('args', {})
    
    try:
        if mutation_name == 'createEntry':
            entry_id = args.get('id', str(uuid4()))
            await FoodEntry.query.create(
                id=entry_id,
                user_id=user_id,
                name=args.get('name', ''),
                price=args.get('price'),
                description=args.get('description', ''),
                image_url=args.get('imageUrl'),
                date=datetime.fromisoformat(args.get('date', datetime.now().isoformat()))
            )
            
        elif mutation_name == 'updateEntry':
            entry_id = args.get('id')
            updates = {}
            
            if 'name' in args:
                updates['name'] = args['name']
            if 'price' in args:
                updates['price'] = args['price']
            if 'description' in args:
                updates['description'] = args['description']
            if 'imageUrl' in args:
                updates['image_url'] = args['imageUrl']
            if 'date' in args:
                updates['date'] = datetime.fromisoformat(args['date'])
            
            await FoodEntry.query.filter(id=entry_id, user_id=user_id).update(**updates)
            
        elif mutation_name == 'deleteEntry':
            entry_id = args.get('id')
            await FoodEntry.query.filter(id=entry_id, user_id=user_id).delete()
            
    except Exception as e:
        logger.error(f"Error processing food mutation {mutation_name}: {e}")
        raise

async def get_food_patch(user_id: str) -> List[Dict[str, Any]]:
    """Get food data for food-tracker-replicache client"""
    try:
        patch = []
        
        entries = await FoodEntry.query.filter(user_id=user_id).all()
        for entry in entries:
            patch.append({
                "op": "put",
                "key": f"food-entry/{entry.id}",
                "value": {
                    "id": str(entry.id),
                    "name": entry.name,
                    "price": entry.price,
                    "description": entry.description,
                    "imageUrl": entry.image_url,
                    "date": entry.date.isoformat() if entry.date else None
                }
            })
        
        return patch
        
    except Exception as e:
        logger.error(f"Error getting food patch: {e}")
        return []

# Diary Context Handlers
async def process_diary_mutation(mutation: Dict[str, Any], user_id: str) -> None:
    """Process diary mutations for diary-replicache client"""
    mutation_name = mutation.get('name', '')
    args = mutation.get('args', {})
    
    try:
        if mutation_name == 'createEntry':
            entry_id = args.get('id', str(uuid4()))
            await DiaryEntry.query.create(
                id=entry_id,
                user_id=user_id,
                title=args.get('title', ''),
                content=args.get('content', ''),
                mood_id=args.get('moodId'),
                date=date.fromisoformat(args.get('date', date.today().isoformat()))
            )
            
        elif mutation_name == 'updateEntry':
            entry_id = args.get('id')
            updates = {}
            
            if 'title' in args:
                updates['title'] = args['title']
            if 'content' in args:
                updates['content'] = args['content']
            if 'moodId' in args:
                updates['mood_id'] = args['moodId']
            if 'date' in args:
                updates['date'] = date.fromisoformat(args['date'])
            
            await DiaryEntry.query.filter(id=entry_id, user_id=user_id).update(**updates)
            
        elif mutation_name == 'deleteEntry':
            entry_id = args.get('id')
            await DiaryEntry.query.filter(id=entry_id, user_id=user_id).delete()
            
    except Exception as e:
        logger.error(f"Error processing diary mutation {mutation_name}: {e}")
        raise

async def get_diary_patch(user_id: str) -> List[Dict[str, Any]]:
    """Get diary data for diary-replicache client"""
    try:
        patch = []
        
        entries = await DiaryEntry.query.filter(user_id=user_id).all()
        for entry in entries:
            patch.append({
                "op": "put",
                "key": f"diary-entry/{entry.id}",
                "value": {
                    "id": str(entry.id),
                    "title": entry.title,
                    "content": entry.content,
                    "moodId": str(entry.mood_id) if entry.mood_id else None,
                    "date": entry.date.isoformat() if entry.date else None,
                    "createdAt": entry.created_at.isoformat() if entry.created_at else None,
                    "updatedAt": entry.updated_at.isoformat() if entry.updated_at else None
                }
            })
        
        return patch
        
    except Exception as e:
        logger.error(f"Error getting diary patch: {e}")
        return []

# Ideas Context Handlers
async def process_ideas_mutation(mutation: Dict[str, Any], user_id: str) -> None:
    """Process ideas mutations for ideas-replicache client"""
    mutation_name = mutation.get('name', '')
    args = mutation.get('args', {})
    
    try:
        if mutation_name == 'createIdea':
            idea_id = args.get('id', str(uuid4()))
            await Idea.query.create(
                id=idea_id,
                user_id=user_id,
                title=args.get('title', ''),
                description=args.get('description', ''),
                category_id=args.get('categoryId'),
                tags=args.get('tags', []),
                is_archived=args.get('isArchived', False)
            )
            
        elif mutation_name == 'updateIdea':
            idea_id = args.get('id')
            updates = {}
            
            if 'title' in args:
                updates['title'] = args['title']
            if 'description' in args:
                updates['description'] = args['description']
            if 'categoryId' in args:
                updates['category_id'] = args['categoryId']
            if 'tags' in args:
                updates['tags'] = args['tags']
            if 'isArchived' in args:
                updates['is_archived'] = args['isArchived']
            
            await Idea.query.filter(id=idea_id, user_id=user_id).update(**updates)
            
        elif mutation_name == 'deleteIdea':
            idea_id = args.get('id')
            await Idea.query.filter(id=idea_id, user_id=user_id).delete()
            
    except Exception as e:
        logger.error(f"Error processing ideas mutation {mutation_name}: {e}")
        raise

async def get_ideas_patch(user_id: str) -> List[Dict[str, Any]]:
    """Get ideas data for ideas-replicache client"""
    try:
        patch = []
        
        ideas = await Idea.query.filter(user_id=user_id).all()
        for idea in ideas:
            patch.append({
                "op": "put",
                "key": f"idea/{idea.id}",
                "value": {
                    "id": str(idea.id),
                    "title": idea.title,
                    "description": idea.description,
                    "categoryId": str(idea.category_id) if idea.category_id else None,
                    "tags": idea.tags or [],
                    "isArchived": idea.is_archived,
                    "createdAt": idea.created_at.isoformat() if idea.created_at else None,
                    "updatedAt": idea.updated_at.isoformat() if idea.updated_at else None
                }
            })
        
        return patch
        
    except Exception as e:
        logger.error(f"Error getting ideas patch: {e}")
        return [] 