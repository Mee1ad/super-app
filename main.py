from esmerald import Esmerald, Gateway, get
from edgy import Database

from core.config import settings
from db.session import database
from apps.todo.endpoints import ListHandler, TaskHandler, ShoppingItemHandler, SearchHandler


@get(path="/ping")
def ping() -> dict:
    return {"message": "pong"}


# Create handlers with database dependency
list_handler = ListHandler(database)
task_handler = TaskHandler(database)
shopping_item_handler = ShoppingItemHandler(database)
search_handler = SearchHandler(database)


app = Esmerald(
    routes=[
        Gateway(handler=ping),
        Gateway(handler=list_handler),
        Gateway(handler=task_handler),
        Gateway(handler=shopping_item_handler),
        Gateway(handler=search_handler),
    ],
    enable_openapi=True,
    title="LifeHub API",
    version="1.0.0",
    description="A comprehensive todo and shopping list API",
) 