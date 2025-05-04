import asyncio

from aiohttp import web, WSMsgType

from config import config


class WebsocketApp(web.Application):
    active_connections = set()

    def __init__(self):
        super().__init__()
        self.add_routes([web.get('/ws', self.websocket_handler)])

    async def websocket_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self.active_connections.add(ws)

        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    pass
                    # if msg.data == 'close':
                    #     await ws.close()
                    # else:
                    #     await ws.send_str(msg.data + '/answer')
                elif msg.type == WSMsgType.ERROR:
                    print('ws connection closed with exception %s' %
                          ws.exception())
        finally:
            self.active_connections.discard(ws)

        print('websocket connection closed')
        return ws

    def broadcast(self, message):
        for ws in self.active_connections:
            if ws.closed:
                self.active_connections.discard(ws)
                continue

            asyncio.create_task(self.send(ws, message))

    async def send(self, ws, message):
        try:
            await ws.send_json(message)
        except Exception as e:
            print(f"Error sending message to client: {e}")


def setup():
    return WebsocketApp()


async def run(app, port=config.websocket_port):
    print(f"Starting Websocket server on port {port}.")
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', port)
    await site.start()
