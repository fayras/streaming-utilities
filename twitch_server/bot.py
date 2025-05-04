import asyncio

from twitchAPI.twitch import Twitch
from twitchAPI.type import ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage
from commands import parse
from config import config

from db import insert_command_in_db


class Bot:
    def __init__(self, twitch_api, websocket):
        self.chat = None
        self.twitch_api = twitch_api
        self.websocket = websocket

    async def handle_message(self, msg: ChatMessage):
        print(f'{msg.user.display_name}: {msg.text}')
        command = parse(msg)
        if command:
            insert_command_in_db(command, msg.user)
            self.websocket.broadcast(command.to_dict())
            await command.execute(msg)

        elif command is None:
            self.websocket.broadcast({
                "command": "chat_message",
                "message": msg.text,
                "username": msg.user.display_name,
                "user_color": msg.user.color
            })

    async def handle_ready(self, ready_event: EventData):
        print('Bot is ready for work, joining channels')
        await ready_event.chat.join_room(config.twitch_target_channel)

    async def run(self):
        chat = await Chat(self.twitch_api)
        chat.register_event(ChatEvent.READY, self.handle_ready)
        chat.register_event(ChatEvent.MESSAGE, self.handle_message)
        # chat.register_event(ChatEvent.SUB, on_sub)

        chat.start()

        try:
            while True:
                await asyncio.sleep(1)
        finally:
            chat.stop()
            await self.twitch_api.close()


async def run(twitch: Twitch, runner):
    bot = Bot(twitch, runner)
    await bot.run()
