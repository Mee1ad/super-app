from esmerald import Esmerald, Gateway, get
from edgy import Database

from core.config import settings
from db.session import database
from apps.todo.endpoints import todo_router


@get(path="/ping")
def ping() -> dict:
    return {"message": "pong"}


app = Esmerald(
    routes=[
        Gateway(handler=ping),
        todo_router,
    ],
    enable_openapi=True,
    title="LifeHub API",
    version="1.0.0",
    description="A comprehensive todo and shopping list API",
) 