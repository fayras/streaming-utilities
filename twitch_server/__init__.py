from dotenv import dotenv_values
from functools import partial

from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
import asyncio

from aiohttp import web, WSMsgType
import threading

from commands import parse
from commands.discord_command import DiscordCommand
from commands.list_command import ListCommand

env_value = dotenv_values(".env")

APP_ID = env_value["TWITCH_APP_ID"]
APP_SECRET = env_value["TWITCH_APP_SECRET"]
TARGET_CHANNEL = env_value["TWITCH_CHANNEL"]
REDIRECT_URI = env_value["TWITCH_REDIRECT_URI"]
USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]


class BroadcastingRunner(web.AppRunner):
    broadcast = lambda *args: None


def aiohttp_server():
    active_connections = set()

    async def websocket_handler(request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        active_connections.add(ws)

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
            active_connections.discard(ws)

        print('websocket connection closed')
        return ws

    # Create a function to broadcast messages
    async def send(ws, message):
        try:
            await ws.send_json(message)
        except Exception as e:
            print(f"Error sending message to client: {e}")

    def broadcast(message):
        for ws in active_connections:
            if ws.closed:
                active_connections.discard(ws)
                continue

            asyncio.create_task(send(ws, message))

    app = web.Application()
    app.add_routes([web.get('/ws', websocket_handler)])
    runner = BroadcastingRunner(app)
    runner.broadcast = broadcast
    return runner


def run_server(runner):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, 'localhost', 8080)
    loop.run_until_complete(site.start())
    loop.run_forever()


# this will be called whenever a message in a channel was sent by either the bot OR another user
async def handle_message(runner, msg: ChatMessage):
    print(f'{msg.user.name}: {msg.text}')
    command = parse(msg)
    if command:
        runner.broadcast(command.to_dict())

        if isinstance(command, DiscordCommand):
            await command.execute(msg)

        if isinstance(command, ListCommand):
            await command.execute(msg)
    elif command is None:
        runner.broadcast({
            "command": "chat_message",
            "message": msg.text,
            "username": msg.user.display_name,
        })


# this will be called when the event READY is triggered, which will be on bot start
async def bot_ready(ready_event: EventData):
    print('Bot is ready for work, joining channels')
    # join our target channel, if you want to join multiple, either call join for each individually
    # or even better pass a list of channels as the argument
    await ready_event.chat.join_room(TARGET_CHANNEL)
    # you can do other bot initialization things in here


# this is where we set up the bot
async def run(runner):
    # set up twitch api instance and add user authentication with some scopes
    twitch = await Twitch(APP_ID, APP_SECRET)
    auth = UserAuthenticator(twitch, USER_SCOPE,
                             url="http://localhost:8990",
                             port=8990)
    token, refresh_token = await auth.authenticate()
    await twitch.set_user_authentication(token, USER_SCOPE, refresh_token)

    # create chat instance
    chat = await Chat(twitch)

    # register the handlers for the events you want

    # listen to when the bot is done starting up and ready to join channels
    chat.register_event(ChatEvent.READY, bot_ready)
    # listen to chat messages
    handle_message_with_runner = partial(handle_message, runner)
    chat.register_event(ChatEvent.MESSAGE, handle_message_with_runner)
    # listen to channel subscriptions
    # chat.register_event(ChatEvent.SUB, on_sub)
    # there are more events, you can view them all in this documentation

    # you can directly register commands and their handlers, this will register the !reply command
    # chat.register_command('reply', test_command)

    # we are done with our setup, lets start this bot up!
    chat.start()

    # Let's run until we press "Enter" in the console
    try:
        input('press ENTER to stop\n')
    finally:
        # now we can close the chatbot and the twitch api client
        chat.stop()
        await twitch.close()


def start_twitch_server():
    runner = aiohttp_server()
    t = threading.Thread(target=run_server, args=(runner,))
    t.daemon = True
    t.start()
    asyncio.run(run(runner))
