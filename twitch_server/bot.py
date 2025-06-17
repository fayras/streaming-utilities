import asyncio
import shlex
from typing import Union

from twitchAPI.twitch import Twitch
from twitchAPI.type import ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage
from commands import BaseCommand, get_all_commands
from config import config

from db import insert_command_in_db, get_user_id
from twitch_server.webserver import WebsocketManager


class Bot:
    def __init__(self, twitch_api, websocket_manager: WebsocketManager):
        self.chat = None
        self.twitch_api = twitch_api
        self.websocket = websocket_manager
        self.all_commands = get_all_commands()

    def parse(self, chat_message: ChatMessage) -> Union[
        BaseCommand, False, None]:
        chat_str = chat_message.text
        if not chat_str.startswith("!"):
            return None

        chat_str_without_exclamation_mark = chat_str[1:]
        tokens = shlex.split(chat_str_without_exclamation_mark)
        if not tokens[0] in self.all_commands:
            return None

        command = self.all_commands[tokens[0]](
            tokens[0], tokens[1:], chat_message
        )
        command.parse(tokens[0], tokens[1:])
        # TODO: Ggf. Fehler werfen, wenn nicht geparsed werden kann und Nachricht
        #       im Twitch Chat schreiben, mit einer "man page"
        if command is None:
            return None

        return command

    async def handle_message(self, msg: ChatMessage):
        print(f'{msg.user.display_name}: {msg.text}')
        command = self.parse(msg)
        if command:
            has_run = await command.run()
            if has_run:
                insert_command_in_db(command, msg.user)
                await self.websocket.broadcast(command.to_dict())

        elif command is None:
            get_user_id(msg.user.name, msg.user.display_name)
            await self.websocket.broadcast({
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


async def run(twitch: Twitch, websocket_manager: WebsocketManager):
    bot = Bot(twitch, websocket_manager)
    await bot.run()
    print("Bot end")
