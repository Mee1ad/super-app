from esmerald import Esmerald, Gateway, get
from edgy import Database

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
    enable_openapi=True,
    title="LifeHub API",
    version="1.0.0",
    description="A comprehensive todo and shopping list API",
) 