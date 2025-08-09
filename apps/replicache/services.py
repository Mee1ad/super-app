import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from uuid import uuid4
import hashlib

from apps.todo.models import List as TodoList, Task, ShoppingItem
from apps.food_tracker.models import FoodEntry
from apps.diary.models import DiaryEntry
from apps.ideas.models import Idea

logger = logging.getLogger(__name__)

def convert_to_uuid(id_str: str, mutation_index: int = 0) -> str:
    """Convert any string ID to a valid UUID using hash, with index to ensure uniqueness"""
    if not id_str:
        return str(uuid4())
    
    # If it's already a valid UUID, return as is (no conversion needed)
    try:
        import uuid
        uuid.UUID(id_str)
        logger.info(f"ID '{id_str}' is already a valid UUID, using as-is")
        return id_str
    except ValueError:
        # Convert to UUID using hash, with index to ensure uniqueness for duplicates
        hash_input = f"{id_str}_{mutation_index}"
        hash_obj = hashlib.md5(hash_input.encode())
        hash_hex = hash_obj.hexdigest()
        # Format as UUID
        uuid_str = f"{hash_hex[:8]}-{hash_hex[8:12]}-{hash_hex[12:16]}-{hash_hex[16:20]}-{hash_hex[20:32]}"
        logger.info(f"Converted ID '{id_str}' (index {mutation_index}) to UUID: {uuid_str}")
        return uuid_str

# Todo Context Handlers
async def process_todo_mutation(
    mutation: Dict[str, Any],
    user_id: str,
    mutation_index: int = 0,
    applied_mutation_id: Optional[int] = None,
) -> None:
    """Process todo mutations for todo-replicache-flat client"""
    mutation_name = mutation.get('name', '')
    args = mutation.get('args', {})
    
    logger.info(f"Processing todo mutation: {mutation_name} with args: {args}")
    
    try:
        # Use the actual mutation id when available for row versioning
        try:
            effective_mutation_id = int(applied_mutation_id if applied_mutation_id is not None else mutation.get('id', mutation_index + 1))
        except Exception:
            effective_mutation_id = mutation_index + 1
        if mutation_name == 'createList':
            # Create new todo list
            list_id = convert_to_uuid(args.get('id', str(uuid4())), mutation_index)
            title = args.get('title', '')
            list_type = args.get('type', 'task')
            variant = args.get('variant', 'default')
            
            logger.info(f"Creating todo list: id={list_id}, title='{title}', type={list_type}, variant={variant}")
            
            # Check if list already exists
            try:
                existing_list = await TodoList.query.get(id=list_id, user_id=user_id)
                if existing_list:
                    logger.warning(f"TodoList with id {list_id} already exists, skipping creation")
                    return
            except Exception as e:
                logger.info(f"List not found, proceeding with creation: {e}")
            
            try:
                await TodoList.query.create(
                    id=list_id,
                    user_id=user_id,
                    title=title,
                    type=list_type,
                    variant=variant
                )
                logger.info(f"Successfully created TodoList: {list_id}")
            except Exception as e:
                if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
                    logger.warning(f"TodoList with id {list_id} already exists, skipping creation")
                else:
                    logger.error(f"Error creating TodoList: {e}")
                    raise
            # Set row version to latest mutation id if column exists
            try:
                await TodoList.query.filter(id=list_id, user_id=user_id).update(last_mutation_id=effective_mutation_id)
            except Exception:
                pass
                    
        elif mutation_name == 'createTask':
            # Create new todo task
            task_id = convert_to_uuid(args.get('id', str(uuid4())), mutation_index)
            list_id = convert_to_uuid(args.get('list_id'), mutation_index) if args.get('list_id') else None
            title = args.get('title', '')
            description = args.get('description')
            checked = args.get('checked', False)
            position = args.get('position', 0)
            variant = args.get('variant', 'default')
            
            logger.info(f"Creating todo task: id={task_id}, list_id={list_id}, title='{title}', description='{description}', checked={checked}, position={position}, variant={variant}")
            
            # Check if task already exists
            try:
                existing_task = await Task.query.get(id=task_id, user_id=user_id)
                if existing_task:
                    logger.warning(f"Task with id {task_id} already exists, skipping creation")
                    return
            except Exception as e:
                logger.info(f"Task not found, proceeding with creation: {e}")
            
            try:
                await Task.query.create(
                    id=task_id,
                    user_id=user_id,
                    list=list_id,
                    title=title,
                    description=description,
                    checked=checked,
                    position=position,
                    variant=variant
                )
                logger.info(f"Successfully created Task: {task_id}")
            except Exception as e:
                if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
                    logger.warning(f"Task with id {task_id} already exists, skipping creation")
                else:
                    logger.error(f"Error creating Task: {e}")
                    raise
            # Set row version to latest mutation id if column exists
            try:
                await Task.query.filter(id=task_id, user_id=user_id).update(last_mutation_id=effective_mutation_id)
            except Exception:
                pass
                    
        elif mutation_name == 'createItem':
            # Create new todo item
            item_id = convert_to_uuid(args.get('id', str(uuid4())), mutation_index)
            list_id = convert_to_uuid(args.get('listId'), mutation_index) if args.get('listId') else None
            title = args.get('title', '')
            completed = args.get('completed', False)
            order = args.get('order', 0)
            
            logger.info(f"Creating todo item: id={item_id}, list_id={list_id}, title='{title}', completed={completed}, order={order}")
            
            # Check if item already exists
            try:
                existing_task = await Task.query.get(id=item_id, user_id=user_id)
                if existing_task:
                    logger.warning(f"Task with id {item_id} already exists, skipping creation")
                    return
            except Exception:
                try:
                    existing_item = await ShoppingItem.query.get(id=item_id, user_id=user_id)
                    if existing_item:
                        logger.warning(f"ShoppingItem with id {item_id} already exists, skipping creation")
                        return
                except Exception:
                    logger.info(f"Item not found, proceeding with creation")
            
            # Determine if it's a task or shopping item based on list type
            try:
                list_obj = await TodoList.query.get(id=list_id, user_id=user_id)
                logger.info(f"Found list: {list_obj.type}")
            except Exception as e:
                logger.error(f"List not found: {list_id} for user {user_id}, error: {e}")
                # Default to task type if list is not found
                list_obj = type('obj', (object,), {'type': 'task'})()
            
            if list_obj.type == 'task':
                logger.info(f"Creating Task with id: {item_id}")
                try:
                    await Task.query.create(
                        id=item_id,
                        user_id=user_id,
                        list=list_id,
                        title=title,
                        checked=completed,
                        position=order
                    )
                    logger.info(f"Successfully created Task: {item_id}")
                except Exception as e:
                    if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
                        logger.warning(f"Task with id {item_id} already exists, skipping creation")
                    else:
                        logger.error(f"Error creating Task: {e}")
                        raise
                # Set row version to latest mutation id if column exists
                try:
                    await Task.query.filter(id=item_id, user_id=user_id).update(last_mutation_id=mutation_index + 1)
                except Exception:
                    pass
            else:  # shopping
                logger.info(f"Creating ShoppingItem with id: {item_id}")
                try:
                    await ShoppingItem.query.create(
                        id=item_id,
                        user_id=user_id,
                        list=list_id,
                        title=title,
                        checked=completed,
                        position=order
                    )
                    logger.info(f"Successfully created ShoppingItem: {item_id}")
                except Exception as e:
                    if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
                        logger.warning(f"ShoppingItem with id {item_id} already exists, skipping creation")
                    else:
                        logger.error(f"Error creating ShoppingItem: {e}")
                        raise
            # Optional: track items too if you later add column
                
        elif mutation_name == 'updateItem':
            # Update existing todo item
            item_id = convert_to_uuid(args.get('id'), mutation_index)
            updates = {}
            
            logger.info(f"Updating todo item: id={item_id}")
            
            if 'title' in args:
                updates['title'] = args['title']
            if 'completed' in args:
                updates['checked'] = args['completed']
            if 'order' in args:
                updates['position'] = args['order']
            
            logger.info(f"Updates to apply: {updates}")
            
            # Try to update as task first, then shopping item
            try:
                await Task.query.filter(id=item_id, user_id=user_id).update(**updates)
                logger.info(f"Successfully updated Task: {item_id}")
            except Exception as e:
                logger.info(f"Task update failed, trying ShoppingItem: {e}")
                await ShoppingItem.query.filter(id=item_id, user_id=user_id).update(**updates)
                logger.info(f"Successfully updated ShoppingItem: {item_id}")
            # Set row version to latest mutation id if column exists
            try:
                await Task.query.filter(id=item_id, user_id=user_id).update(last_mutation_id=effective_mutation_id)
            except Exception:
                pass
                
        elif mutation_name == 'deleteItem':
            # Delete todo item
            item_id = convert_to_uuid(args.get('id'), mutation_index)
            
            logger.info(f"Deleting todo item: id={item_id}")
            
            # Try to delete as task first, then shopping item
            try:
                await Task.query.filter(id=item_id, user_id=user_id).delete()
                logger.info(f"Successfully deleted Task: {item_id}")
            except Exception as e:
                logger.info(f"Task delete failed, trying ShoppingItem: {e}")
                await ShoppingItem.query.filter(id=item_id, user_id=user_id).delete()
                logger.info(f"Successfully deleted ShoppingItem: {item_id}")
                
    except Exception as e:
        logger.error(f"Error processing todo mutation {mutation_name}: {e}", exc_info=True)
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
async def process_food_mutation(mutation: Dict[str, Any], user_id: str, mutation_index: int = 0) -> None:
    """Process food mutations for food-tracker-replicache client"""
    mutation_name = mutation.get('name', '')
    args = mutation.get('args', {})
    
    logger.info(f"Processing food mutation: {mutation_name} with args: {args}")
    
    try:
        if mutation_name == 'createEntry':
            entry_id = convert_to_uuid(args.get('id', str(uuid4())), mutation_index)
            name = args.get('name', '')
            price = args.get('price')
            description = args.get('description', '')
            image_url = args.get('imageUrl')
            date_str = args.get('date', datetime.now().isoformat())
            meal_type = args.get('mealType')
            time = args.get('time')
            
            logger.info(f"Creating food entry: id={entry_id}, name='{name}', price={price}, description='{description}', image_url={image_url}, date={date_str}, mealType={meal_type}, time={time}")
            
            # Check if entry already exists
            try:
                existing_entry = await FoodEntry.query.get(id=entry_id, user_id=user_id)
                if existing_entry:
                    logger.warning(f"FoodEntry with id {entry_id} already exists, skipping creation")
                    return
            except Exception as e:
                logger.info(f"Entry not found, proceeding with creation: {e}")
            
            # Combine date and time if both are provided
            if date_str and time:
                try:
                    # Parse the date and time
                    date_obj = datetime.fromisoformat(date_str)
                    time_parts = time.split(':')
                    if len(time_parts) == 2:
                        hour, minute = int(time_parts[0]), int(time_parts[1])
                        combined_datetime = date_obj.replace(hour=hour, minute=minute)
                        date_str = combined_datetime.isoformat()
                        logger.info(f"Combined date and time: {date_str}")
                except Exception as e:
                    logger.warning(f"Failed to combine date and time: {e}, using date only")
            
            try:
                await FoodEntry.query.create(
                    id=entry_id,
                    user_id=user_id,
                    name=name,
                    price=price,
                    description=description,
                    image_url=image_url,
                    date=datetime.fromisoformat(date_str)
                )
                logger.info(f"Successfully created FoodEntry: {entry_id}")
            except Exception as e:
                if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
                    logger.warning(f"FoodEntry with id {entry_id} already exists, skipping creation")
                else:
                    logger.error(f"Error creating FoodEntry: {e}")
                    raise
            
        elif mutation_name == 'updateEntry':
            entry_id = convert_to_uuid(args.get('id'), mutation_index)
            updates = {}
            
            logger.info(f"Updating food entry: id={entry_id}")
            
            if 'name' in args:
                updates['name'] = args['name']
            if 'price' in args:
                updates['price'] = args['price']
            if 'description' in args:
                updates['description'] = args['description']
            if 'imageUrl' in args:
                updates['image_url'] = args['imageUrl']
            if 'date' in args:
                date_str = args['date']
                time = args.get('time')
                
                # Combine date and time if both are provided
                if date_str and time:
                    try:
                        date_obj = datetime.fromisoformat(date_str)
                        time_parts = time.split(':')
                        if len(time_parts) == 2:
                            hour, minute = int(time_parts[0]), int(time_parts[1])
                            combined_datetime = date_obj.replace(hour=hour, minute=minute)
                            date_str = combined_datetime.isoformat()
                            logger.info(f"Combined date and time for update: {date_str}")
                    except Exception as e:
                        logger.warning(f"Failed to combine date and time for update: {e}, using date only")
                
                updates['date'] = datetime.fromisoformat(date_str)
            
            logger.info(f"Updates to apply: {updates}")
            
            await FoodEntry.query.filter(id=entry_id, user_id=user_id).update(**updates)
            logger.info(f"Successfully updated FoodEntry: {entry_id}")
            
        elif mutation_name == 'deleteEntry':
            entry_id = convert_to_uuid(args.get('id'), mutation_index)
            
            logger.info(f"Deleting food entry: id={entry_id}")
            
            await FoodEntry.query.filter(id=entry_id, user_id=user_id).delete()
            logger.info(f"Successfully deleted FoodEntry: {entry_id}")
            
    except Exception as e:
        logger.error(f"Error processing food mutation {mutation_name}: {e}", exc_info=True)
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
async def process_diary_mutation(mutation: Dict[str, Any], user_id: str, mutation_index: int = 0) -> None:
    """Process diary mutations for diary-replicache client"""
    mutation_name = mutation.get('name', '')
    args = mutation.get('args', {})
    
    try:
        if mutation_name == 'createEntry':
            entry_id = convert_to_uuid(args.get('id', str(uuid4())), mutation_index)
            await DiaryEntry.query.create(
                id=entry_id,
                user_id=user_id,
                title=args.get('title', ''),
                content=args.get('content', ''),
                mood_id=convert_to_uuid(args.get('moodId'), mutation_index) if args.get('moodId') else None,
                date=date.fromisoformat(args.get('date', date.today().isoformat()))
            )
            
        elif mutation_name == 'updateEntry':
            entry_id = convert_to_uuid(args.get('id'), mutation_index)
            updates = {}
            
            if 'title' in args:
                updates['title'] = args['title']
            if 'content' in args:
                updates['content'] = args['content']
            if 'moodId' in args:
                updates['mood_id'] = convert_to_uuid(args['moodId'], mutation_index)
            if 'date' in args:
                updates['date'] = date.fromisoformat(args['date'])
            
            await DiaryEntry.query.filter(id=entry_id, user_id=user_id).update(**updates)
            
        elif mutation_name == 'deleteEntry':
            entry_id = convert_to_uuid(args.get('id'), mutation_index)
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
async def process_ideas_mutation(mutation: Dict[str, Any], user_id: str, mutation_index: int = 0) -> None:
    """Process ideas mutations for ideas-replicache client"""
    mutation_name = mutation.get('name', '')
    args = mutation.get('args', {})
    
    try:
        if mutation_name == 'createIdea':
            idea_id = convert_to_uuid(args.get('id', str(uuid4())), mutation_index)
            await Idea.query.create(
                id=idea_id,
                user_id=user_id,
                title=args.get('title', ''),
                description=args.get('description', ''),
                category_id=convert_to_uuid(args.get('categoryId'), mutation_index) if args.get('categoryId') else None,
                tags=args.get('tags', []),
                is_archived=args.get('isArchived', False)
            )
            
        elif mutation_name == 'updateIdea':
            idea_id = convert_to_uuid(args.get('id'), mutation_index)
            updates = {}
            
            if 'title' in args:
                updates['title'] = args['title']
            if 'description' in args:
                updates['description'] = args['description']
            if 'categoryId' in args:
                updates['category_id'] = convert_to_uuid(args['categoryId'], mutation_index)
            if 'tags' in args:
                updates['tags'] = args['tags']
            if 'isArchived' in args:
                updates['is_archived'] = args['isArchived']
            
            await Idea.query.filter(id=idea_id, user_id=user_id).update(**updates)
            
        elif mutation_name == 'deleteIdea':
            idea_id = convert_to_uuid(args.get('id'), mutation_index)
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