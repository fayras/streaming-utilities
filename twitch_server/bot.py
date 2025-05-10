import asyncio
import shlex
from typing import Union

from twitchAPI.twitch import Twitch
from twitchAPI.type import ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage
from commands import BaseCommand, get_all_commands
from config import config

from db import insert_command_in_db


class Bot:
    def __init__(self, twitch_api, websocket):
        self.chat = None
        self.twitch_api = twitch_api
        self.websocket = websocket
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
        # TODO: Ggf. Fehler werfen, wenn nicht geparsed werden kann und Nachricht
        #       im Twitch Chat schreiben, mit einer "man page"
        if command is None:
            return None

        # TODO: Anstatt "check_cooldown" sollte die jeweilige Middleware eine
        #       Nachricht ausgeben.

        # if command.check_cooldown(chat_user):
        #     os.system(
        #         f'notify-send "Command noch auf Cooldown" "@{chat_user.name} {chat_str}"'
        #     )
        #     return False

        return command

    async def handle_message(self, msg: ChatMessage):
        print(f'{msg.user.display_name}: {msg.text}')
        command = self.parse(msg)
        if command:
            insert_command_in_db(command, msg.user)
            self.websocket.broadcast(command.to_dict())
            await command.run()

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
