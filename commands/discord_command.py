from typing import Self, Any, override

from config import config
from twitchAPI.chat import ChatMessage
from commands.base_command import BaseCommand, ChatUser


class DiscordCommand(BaseCommand):
    name = "discord"
    aliases = ["dc"]
    global_cooldown = 30

    @override
    async def execute(self, chat_message: ChatMessage) -> None:
        await chat_message.reply(config.discord_invite_link)

    @override
    def parse(self, _, params: list[str], user: ChatUser) -> Self | None:
        return self

    @override
    def get_params(self) -> dict[str, Any]:
        pass
