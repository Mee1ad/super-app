from esmerald import Esmerald, Gateway, get, CORSConfig
from core.config import settings
from db.session import database
from apps.todo.endpoints import (
    get_lists, create_list, update_list, delete_list,
    get_tasks, create_task, update_task, delete_task, toggle_task, reorder_tasks,
    get_items, create_item, update_item, delete_item, toggle_item, reorder_items,
    search
)

@get(path="/ping")
def ping() -> dict:
    return {"message": "pong"}

# Robust CORS configuration
cors_config = CORSConfig(
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    max_age=3600,
)

app = Esmerald(
    routes=[
        Gateway(handler=ping),
        get_lists,
        create_list,
        update_list,
        delete_list,
        get_tasks,
        create_task,
        update_task,
        delete_task,
        toggle_task,
        reorder_tasks,
        get_items,
        create_item,
        update_item,
        delete_item,
        toggle_item,
        reorder_items,
        search,
    ],
    cors_config=cors_config,
    enable_openapi=True,
    openapi_url="/openapi",
    title="LifeHub API",
    version="1.0.0",
    description="A comprehensive REST API for managing todo lists and shopping lists with JWT authentication, real-time search, and bulk operations.",
)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect() 