from esmerald import Esmerald, Gateway, get

@get(path="/ping")
def ping() -> dict:
    return {"message": "pong"}

app = Esmerald(
    routes=[Gateway(handler=ping)],
) 