import socket
from contextlib import closing
from typing import Set

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from twitchAPI.twitch import Twitch

from config import config
from db import query


class WebsocketManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active_connections.add(ws)

    def disconnect(self, ws: WebSocket):
        self.active_connections.remove(ws)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


def setup(twitch: Twitch):
    app = FastAPI()
    ws_manager = WebsocketManager()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:80",
            "http://localhost:5173",
            "http://localhost:4173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.websocket("/ws/{client_id}")
    async def websocket(ws: WebSocket, client_id: str):
        await ws_manager.connect(ws)
        print(f"Client \"{client_id}\" connected")
        try:
            while True:
                await ws.receive_text()
        except WebSocketDisconnect:
            ws_manager.disconnect(ws)
            print(f"Client \"{client_id}\" disconnected")

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

    return app, ws_manager


def check_port(port=8080):
    """Try preferred port first, otherwise let system choose"""
    try:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', port))
            return True
    except OSError:
        return False


async def run(app: FastAPI, port=config.webserver_port):
    available_port = port if check_port(port) else 0
    server_config = uvicorn.Config(
        app,
        port=available_port,
        log_level="warning"
    )
    server = uvicorn.Server(server_config)
    print(f"Starting web server on port {available_port}.")
    await server.serve()
    print("Webserver end")
