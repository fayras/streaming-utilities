from typing import Self, Any

from twitchAPI.chat import ChatMessage
from dotenv import dotenv_values

from commands.base_command import BaseCommand, ChatUser


class DiscordCommand(BaseCommand):
    name = "discord"
    global_cooldown = 30

    async def execute(self, chat_message: ChatMessage) -> None:
        discord_link = dotenv_values(".env")["DISCORD_INVITE_LINK"]
        await chat_message.reply(discord_link)

    def parse(self, params: list[str], user: ChatUser) -> Self | None:
        return self

    def set_params_from_json(self, json: dict[str, Any]) -> Self | None:
        return self

    def get_params(self) -> dict[str, Any]:
        pass
