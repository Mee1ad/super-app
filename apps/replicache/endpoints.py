from esmerald import Request, Response, get, post, HTTPException, status
from typing import Dict, Set, Any, Optional
import asyncio
import json
import logging
from datetime import datetime, timezone

from edgy import Database

from core.dependencies import get_current_user_dependency

# Import QueueFull exception
from asyncio import QueueFull

# Configure logging
logger = logging.getLogger(__name__)

def create_cookie(user_id: str, client_id: str, last_mutation_id: int, client_name: str) -> str:
    """Create a cookie with current state information"""
    cookie_data = {
        "lastMutationID": last_mutation_id,
        "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),  # milliseconds
        "userId": user_id,
        "clientId": client_id,
        "clientName": client_name
    }
    return json.dumps(cookie_data)

def parse_cookie(cookie: Optional[str]) -> Optional[Dict[str, Any]]:
    """Parse a cookie string into a dictionary"""
    if not cookie:
        return None
    try:
        return json.loads(cookie)
    except (json.JSONDecodeError, TypeError):
        logger.warning(f"Failed to parse cookie: {cookie}")
        return None

class SSEManager:
    """Singleton manager for user-specific SSE connections"""
    
    def __init__(self):
        self.user_connections: Dict[str, Set[asyncio.Queue]] = {}
        self.user_versions: Dict[str, int] = {}
        # Track last mutation IDs per client
        self.client_mutation_ids: Dict[str, Dict[str, int]] = {}
        self._lock = asyncio.Lock()
    
    async def add_client(self, user_id: str, queue: asyncio.Queue) -> None:
        """Register a client for a specific user"""
        async with self._lock:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(queue)
            logger.info(f"User {user_id} connected. Total clients: {len(self.user_connections[user_id])}")
    
    async def remove_client(self, user_id: str, queue: asyncio.Queue) -> None:
        """Remove a client for a specific user"""
        async with self._lock:
            if user_id in self.user_connections:
                self.user_connections[user_id].discard(queue)
                if not self.user_connections[user_id]:
                    self.user_connections.pop(user_id, None)
                    logger.info(f"User {user_id} disconnected. No more clients.")
                else:
                    logger.info(f"User {user_id} client removed. Remaining clients: {len(self.user_connections[user_id])}")
    
    async def notify_user(self, user_id: str, message: str) -> int:
        """Notify all clients for a specific user"""
        try:
            async with self._lock:
                queues = self.user_connections.get(user_id, set())
                notified_count = 0
                logger.info(f"Attempting to notify {len(queues)} clients for user {user_id}")
                
                for queue in queues:
                    try:
                        # Use put_nowait to avoid blocking if queue is full
                        queue.put_nowait(message)
                        notified_count += 1
                        logger.debug(f"Successfully notified client for user {user_id}")
                    except QueueFull:
                        logger.warning(f"Queue full for user {user_id}, skipping notification")
                    except Exception as e:
                        logger.error(f"Failed to notify client for user {user_id}: {e}")
                
                logger.info(f"Notified {notified_count} clients for user {user_id}")
                return notified_count
        except Exception as e:
            logger.error(f"Error in notify_user for user {user_id}: {e}")
            return 0
    
    async def get_user_client_count(self, user_id: str) -> int:
        """Get the number of connected clients for a user"""
        async with self._lock:
            return len(self.user_connections.get(user_id, set()))
    
    async def get_total_connections(self) -> int:
        """Get total number of connections across all users"""
        async with self._lock:
            return sum(len(clients) for clients in self.user_connections.values())
    
    async def get_client_mutation_id(self, user_id: str, client_id: str) -> int:
        """Get the last mutation ID for a specific client"""
        async with self._lock:
            if user_id not in self.client_mutation_ids:
                return 0
            return self.client_mutation_ids[user_id].get(client_id, 0)
    
    async def update_client_mutation_id(self, user_id: str, client_id: str, mutation_id: int) -> None:
        """Update the last mutation ID for a specific client"""
        async with self._lock:
            if user_id not in self.client_mutation_ids:
                self.client_mutation_ids[user_id] = {}
            self.client_mutation_ids[user_id][client_id] = mutation_id
            logger.info(f"Updated mutation ID for user {user_id}, client {client_id}: {mutation_id}")
    
    async def get_last_mutation_id_changes(self, user_id: str) -> Dict[str, int]:
        """Get the last mutation ID changes for a user"""
        async with self._lock:
            return self.client_mutation_ids.get(user_id, {})

# Global SSE manager instance
sse_manager = SSEManager()

# SSE stream endpoint
@get(
    tags=["Replicache"],
    summary="SSE stream for user-specific notifications",
    description="Server-Sent Events stream for user-specific real-time notifications"
)
async def sse_stream(request: Request) -> Response:
    """SSE stream endpoint for user-specific notifications"""
    try:
        # Get user from JWT token
        user = await get_current_user_dependency(request)
        user_id = str(user.id)
        
        # Create queue for this client with larger size
        queue = asyncio.Queue(maxsize=100)
        
        # Register client
        await sse_manager.add_client(user_id, queue)
        
        logger.info(f"SSE stream started for user {user_id}")
        
        # For now, return a simple response to test if the endpoint works
        # We'll implement proper streaming later
        await sse_manager.remove_client(user_id, queue)
        
        return Response(
            content="data: connected\n\n",
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control"
            }
        )
    
    except HTTPException as e:
        # Re-raise HTTP exceptions (like 401) as-is
        logger.error(f"SSE stream HTTP error: {e.status_code} - {e.detail}")
        raise
    except Exception as e:
        logger.error(f"SSE stream error for user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Stream error")

# Poke endpoint for user-specific notifications
@post(
    tags=["Replicache"],
    summary="Trigger user-specific sync notification",
    description="Notify all connected clients for a specific user"
)
async def poke_user(request: Request) -> Dict[str, Any]:
    """Trigger user-specific sync notification"""
    try:
        user = await get_current_user_dependency(request)
        user_id = str(user.id)
        logger.info(f"Poke request for user: {user_id}")
        
        # Notify user's clients
        notified_count = await sse_manager.notify_user(user_id, "sync")
        
        result = {
            "success": True,
            "userId": user_id,
            "clientsNotified": notified_count,
            "message": "User-specific sync triggered",
            "timestamp": datetime.utcnow().isoformat()
        }
        logger.info(f"Poke successful for user {user_id}: {result}")
        return result
    
    except HTTPException:
        # Re-raise HTTP exceptions (like 401) as-is
        raise
    except Exception as e:
        logger.error(f"Poke error for user: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Poke error: {str(e)}")

# Legacy endpoints (keeping for backward compatibility)
@get(
    tags=["Replicache"],
    summary="SSE events stream (legacy)",
    description="Legacy SSE events stream for Replicache notifications"
)
async def sse_events(request: Request) -> Response:
    """Legacy SSE endpoint - redirects to new stream endpoint"""
    return await sse_stream(request)

@post(
    tags=["Replicache"],
    summary="Poke clients (legacy)",
    description="Legacy poke endpoint - redirects to new poke endpoint"
)
async def poke(request: Request) -> Dict[str, Any]:
    """Legacy poke endpoint - redirects to new poke endpoint"""
    return await poke_user(request)

# Replicache pull
@post(
    tags=["Replicache"],
    summary="Replicache pull",
    description="Get changes since client version",
    status_code=200
)
async def replicache_pull(request: Request) -> Dict[str, Any]:
    user = await get_current_user_dependency(request)
    user_id = str(user.id)
    body = await request.json()
    
    # Debug: Log the request body to see what's being sent
    logger.info(f"Pull request body: {body}")
    
    # Try clientView.name first (correct Replicache v15 format)
    client_name = body.get('clientView', {}).get('name', '')
    client_id = body.get('clientView', {}).get('id', 'default')
    
    # Fallback to clientGroupID if clientView.name is not present (Replicache v14 format)
    if not client_name:
        client_group_id = body.get('clientGroupID', '')
        logger.info(f"Using clientGroupID: '{client_group_id}' (Replicache v14 format)")
        
        # For now, treat all clientGroupIDs as todo context
        # You can customize this mapping based on your frontend configuration
        client_name = 'todo-replicache-flat'
        client_id = client_group_id or 'default'
    
    logger.info(f"Final client name: '{client_name}', client ID: '{client_id}'")
    
    # Parse incoming cookie if provided
    incoming_cookie = body.get('cookie')
    if incoming_cookie:
        parsed_cookie = parse_cookie(incoming_cookie)
        if parsed_cookie:
            logger.info(f"Parsed incoming cookie: {parsed_cookie}")
            # You can use the parsed cookie data for validation or additional logic
    
    # Get the client's last mutation ID
    last_mutation_id = await sse_manager.get_client_mutation_id(user_id, client_id)
    logger.info(f"Client {client_id} last mutation ID: {last_mutation_id}")
    
    # Import services
    from apps.replicache.services import (
        get_todo_patch, get_food_patch, get_diary_patch, get_ideas_patch
    )
    
    # Route data based on client name
    if client_name == 'todo-replicache-flat':
        patch = await get_todo_patch(user_id)
    elif client_name == 'food-tracker-replicache':
        patch = await get_food_patch(user_id)
    elif client_name == 'diary-replicache':
        patch = await get_diary_patch(user_id)
    elif client_name == 'ideas-replicache':
        patch = await get_ideas_patch(user_id)
    else:
        logger.warning(f"Unknown client name: '{client_name}'")
        patch = []
    
    # Get current mutation ID changes for this user
    last_mutation_id_changes = await sse_manager.get_last_mutation_id_changes(user_id)
    
    # Check if we have any changes to report
    has_changes = bool(last_mutation_id_changes) or bool(patch)
    
    # If no changes, return empty lastMutationIDChanges to avoid Replicache error
    if not has_changes:
        last_mutation_id_changes = {}
        # Use the current last_mutation_id for the cookie when no changes
        cookie_last_mutation_id = last_mutation_id
    else:
        # Find the highest mutation ID in the changes to ensure consistency
        if last_mutation_id_changes:
            cookie_last_mutation_id = max(last_mutation_id_changes.values())
        else:
            cookie_last_mutation_id = last_mutation_id
    
    # Create cookie with the correct lastMutationID
    cookie = create_cookie(user_id, client_id, cookie_last_mutation_id, client_name)
    
    return {
        "lastMutationIDChanges": last_mutation_id_changes,
        "cookie": cookie,
        "patch": patch
    }

# Replicache push
@post(
    tags=["Replicache"],
    summary="Replicache push",
    description="Apply mutations and return new version",
    status_code=200
)
async def replicache_push(request: Request) -> Dict[str, Any]:
    user = await get_current_user_dependency(request)
    user_id = str(user.id)
    body = await request.json()
    
    # Debug: Log the request body to see what's being sent
    logger.info(f"Push request body: {body}")
    
    mutations = body.get("mutations", [])
    logger.info(f"Processing {len(mutations)} mutations for user {user_id}")
    
    # Try clientView.name first (correct Replicache v15 format)
    client_name = body.get('clientView', {}).get('name', '')
    client_id = body.get('clientView', {}).get('id', 'default')
    
    # Fallback to clientGroupID if clientView.name is not present (Replicache v14 format)
    if not client_name:
        client_group_id = body.get('clientGroupID', '')
        logger.info(f"Using clientGroupID: '{client_group_id}' (Replicache v14 format)")
        
        # Intelligently detect client type based on mutation names
        if mutations:
            # Check the first mutation to determine client type
            first_mutation_name = mutations[0].get('name', '')
            logger.info(f"Detecting client type from mutation: {first_mutation_name}")
            
            if first_mutation_name in ['createEntry', 'updateEntry', 'deleteEntry']:
                # Check if it's food tracker or diary based on args
                first_args = mutations[0].get('args', {})
                if 'mealType' in first_args or 'name' in first_args:
                    client_name = 'food-tracker-replicache'
                    logger.info(f"Detected food-tracker-replicache based on mutation: {first_mutation_name}")
                else:
                    client_name = 'diary-replicache'
                    logger.info(f"Detected diary-replicache based on mutation: {first_mutation_name}")
            elif first_mutation_name in ['createItem', 'updateItem', 'deleteItem']:
                client_name = 'todo-replicache-flat'
                logger.info(f"Detected todo-replicache-flat based on mutation: {first_mutation_name}")
            elif first_mutation_name in ['createIdea', 'updateIdea', 'deleteIdea']:
                client_name = 'ideas-replicache'
                logger.info(f"Detected ideas-replicache based on mutation: {first_mutation_name}")
            else:
                # Default fallback
                client_name = 'todo-replicache-flat'
                logger.warning(f"Unknown mutation type: {first_mutation_name}, defaulting to todo-replicache-flat")
        else:
            # No mutations, default to todo
            client_name = 'todo-replicache-flat'
            logger.warning("No mutations found, defaulting to todo-replicache-flat")
        
        client_id = client_group_id or 'default'
    
    logger.info(f"Final client name: '{client_name}', client ID: '{client_id}'")
    
    # Parse incoming cookie if provided
    incoming_cookie = body.get('cookie')
    if incoming_cookie:
        parsed_cookie = parse_cookie(incoming_cookie)
        if parsed_cookie:
            logger.info(f"Parsed incoming cookie: {parsed_cookie}")
            # You can use the parsed cookie data for validation or additional logic
            # For example, check if the client's lastMutationID matches what we expect
    
    # Import services
    from apps.replicache.services import (
        process_todo_mutation, process_food_mutation, 
        process_diary_mutation, process_ideas_mutation
    )
    
    # Process mutations by client name
    for i, mutation in enumerate(mutations):
        mutation_name = mutation.get('name', '')
        mutation_id = mutation.get('id', 0)
        args = mutation.get('args', {})
        
        logger.info(f"Processing mutation {i+1}/{len(mutations)}: {mutation_name} with args: {args}")
        
        try:
            # Route by client name instead of mutation prefix
            if client_name == 'todo-replicache-flat':
                logger.info(f"Routing to process_todo_mutation for mutation: {mutation_name}")
                await process_todo_mutation(mutation, user_id, i)
                logger.info(f"Successfully processed todo mutation: {mutation_name}")
            elif client_name == 'food-tracker-replicache':
                logger.info(f"Routing to process_food_mutation for mutation: {mutation_name}")
                await process_food_mutation(mutation, user_id, i)
                logger.info(f"Successfully processed food mutation: {mutation_name}")
            elif client_name == 'diary-replicache':
                logger.info(f"Routing to process_diary_mutation for mutation: {mutation_name}")
                await process_diary_mutation(mutation, user_id, i)
                logger.info(f"Successfully processed diary mutation: {mutation_name}")
            elif client_name == 'ideas-replicache':
                logger.info(f"Routing to process_ideas_mutation for mutation: {mutation_name}")
                await process_ideas_mutation(mutation, user_id, i)
                logger.info(f"Successfully processed ideas mutation: {mutation_name}")
            else:
                logger.warning(f"Unknown client name: '{client_name}'")
            
            # Update the client's last mutation ID
            await sse_manager.update_client_mutation_id(user_id, client_id, mutation_id)
            logger.info(f"Processed mutation {mutation_id} for client {client_id}")
            
        except Exception as e:
            logger.error(f"Error processing mutation {mutation_name}: {e}", exc_info=True)
            # Re-raise the exception to ensure the client knows about the error
            raise
    
    # Update version
    sse_manager.user_versions[user_id] = sse_manager.user_versions.get(user_id, 0) + 1
    logger.info(f"Updated user version to: {sse_manager.user_versions[user_id]}")
    
    # Notify user's clients
    await sse_manager.notify_user(user_id, "sync")
    logger.info(f"Notified user {user_id} about sync")
    
    # Get the updated last mutation ID for this client
    last_mutation_id = await sse_manager.get_client_mutation_id(user_id, client_id)
    
    # Get updated mutation ID changes for this user
    last_mutation_id_changes = await sse_manager.get_last_mutation_id_changes(user_id)
    
    # Find the highest mutation ID in the changes to ensure consistency
    if last_mutation_id_changes:
        cookie_last_mutation_id = max(last_mutation_id_changes.values())
    else:
        cookie_last_mutation_id = last_mutation_id
    
    # Create cookie with the correct lastMutationID
    cookie = create_cookie(user_id, client_id, cookie_last_mutation_id, client_name)
    
    logger.info(f"Push completed successfully. Returning response with cookie: {cookie}")
    
    return {
        "lastMutationIDChanges": last_mutation_id_changes,
        "cookie": cookie
    }

# Debug endpoint to get connection stats
@get(
    tags=["Replicache"],
    summary="Get SSE connection stats",
    description="Get current SSE connection statistics"
)
async def get_sse_stats(request: Request) -> Dict[str, Any]:
    """Get SSE connection statistics"""
    try:
        user = await get_current_user_dependency(request)
        user_id = str(user.id)
        
        user_clients = await sse_manager.get_user_client_count(user_id)
        total_connections = await sse_manager.get_total_connections()
        
        return {
            "userId": user_id,
            "userConnections": user_clients,
            "totalConnections": total_connections,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Stats error")