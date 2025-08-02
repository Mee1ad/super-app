from esmerald import Request, Response, get, post, HTTPException, status
from typing import Dict, Set, Any
import asyncio
import json

from core.dependencies import get_current_user_dependency

# In-memory: user_id -> set of asyncio.Queue (one per client connection)
user_clients: Dict[str, Set[asyncio.Queue]] = {}
# In-memory: user_id -> version (int)
user_versions: Dict[str, int] = {}

# SSE event stream
@get(
    tags=["Replicache"],
    summary="SSE events stream",
    description="Server-Sent Events stream for Replicache notifications"
)
async def sse_events(request: Request) -> Response:
    user = await get_current_user_dependency(request)
    user_id = str(user.id)
    queue = asyncio.Queue()
    user_clients.setdefault(user_id, set()).add(queue)
    
    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=15)
                    yield f"data: {msg}\n\n"
                except asyncio.TimeoutError:
                    yield ": keep-alive\n\n"
        finally:
            user_clients[user_id].discard(queue)
            if not user_clients[user_id]:
                user_clients.pop(user_id, None)
    
    return Response(event_generator(), media_type="text/event-stream")

# Poke endpoint
@post(
    tags=["Replicache"],
    summary="Poke clients",
    description="Notify all connected clients for the user"
)
async def poke(request: Request) -> Dict[str, Any]:
    user = await get_current_user_dependency(request)
    user_id = str(user.id)
    queues = user_clients.get(user_id, set())
    for q in queues:
        await q.put(json.dumps({"type": "poke"}))
    return {"ok": True}

# Replicache pull
@post(
    tags=["Replicache"],
    summary="Replicache pull",
    description="Get changes since client version"
)
async def replicache_pull(request: Request) -> Dict[str, Any]:
    user = await get_current_user_dependency(request)
    user_id = str(user.id)
    body = await request.json()
    client_version = body.get("clientVersion", 0)
    server_version = user_versions.get(user_id, 0)
    response = {
        "changes": [],
        "serverVersion": server_version,
    }
    raise HTTPException(status_code=status.HTTP_200_OK, detail=response)

# Replicache push
@post(
    tags=["Replicache"],
    summary="Replicache push",
    description="Apply mutations and return new version"
)
async def replicache_push(request: Request) -> Dict[str, Any]:
    user = await get_current_user_dependency(request)
    user_id = str(user.id)
    body = await request.json()
    mutations = body.get("mutations", [])
    user_versions[user_id] = user_versions.get(user_id, 0) + 1
    queues = user_clients.get(user_id, set())
    for q in queues:
        await q.put(json.dumps({"type": "poke"}))
    response = {"ok": True, "newVersion": user_versions[user_id]}
    raise HTTPException(status_code=status.HTTP_200_OK, detail=response)