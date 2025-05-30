import asyncio
from collections.abc import Callable, Awaitable
from enum import Enum
from typing import Any

import aiohttp


class WebSocketClient:
    class Status(Enum):
        CREATED = 1
        CONNECTED = 2
        DISCONNECTED = 3
        RETRYING = 4

    def __init__(self,
                 client_id: str,
                 handler: Callable[[Any], Awaitable[None]]
                 ):
        self.id = client_id
        self.message_handler = handler
        self.status = WebSocketClient.Status.CREATED
        self.ws = None

    def get_status(self):
        return self.status

    def is_connected(self):
        return self.ws is not None

    async def start(self):
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(
                            f'http://localhost:8080/ws/{self.id}') as ws:
                        self.ws = ws
                        self.status = WebSocketClient.Status.CONNECTED

                        async for msg in ws:
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                await self.message_handler(msg.data)
                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                print("WebSocket connection error")
                                break
                            elif msg.type == aiohttp.WSMsgType.CLOSED:
                                print("WebSocket connection closed")
                                break

            except aiohttp.ClientError as e:
                self.status = WebSocketClient.Status.DISCONNECTED
            except Exception as e:
                self.status = WebSocketClient.Status.DISCONNECTED

            self.ws = None
            self.status = WebSocketClient.Status.RETRYING
            retry_time = 3
            print(
                f"Attempting to reconnect in {retry_time} seconds...")
            await asyncio.sleep(retry_time)
