import socket
from contextlib import closing

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from twitchAPI.twitch import Twitch

from config import config
from db import query

origins = [
    "http://localhost:80",
    "http://localhost:5173",
    "http://localhost:4173",
]


def setup(twitch: Twitch):
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    @app.get("/users")
    async def users():
        return twitch.get_users()

    @app.get("/votm_winners")
    async def votm_winners():
        result = query("SELECT * FROM viewer_of_the_month_winners", ())
        return result

    return app


def check_port(port=8000):
    """Try preferred port first, otherwise let system choose"""
    try:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            sock.bind(('', port))
            return True
    except OSError:
        return False


async def run(app: FastAPI, port=config.webserver_port):
    print(f"Starting web server on port {port}.")
    available_port = port if check_port(port) else 0
    server_config = uvicorn.Config(app, port=available_port,
                                   log_level="warning")
    server = uvicorn.Server(server_config)
    await server.serve()
