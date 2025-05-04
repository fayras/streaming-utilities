import uvicorn
from fastapi import FastAPI
from twitchAPI.twitch import Twitch

from config import config


def setup(twitch: Twitch):
    app = FastAPI()

    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    @app.get("/users")
    async def users():
        return twitch.get_users()

    return app


async def run(app: FastAPI, port=config.webserver_port):
    print(f"Starting web server on port {port}.")
    server_config = uvicorn.Config(app, port=port, log_level="warning")
    server = uvicorn.Server(server_config)
    await server.serve()
