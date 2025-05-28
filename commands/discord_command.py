from typing import Self, Any, override

from commands.middleware.global_cooldown import GlobalCooldown
from config import config
from commands.base_command import BaseCommand


class DiscordCommand(BaseCommand):
    name = "discord"
    aliases = ["dc"]
    middleware = [GlobalCooldown(30)]

    @override
    async def execute(self) -> None:
        message = f"Komm in die Gruppe! {config.discord_invite_link}"
        await self.chat_message.reply(message)

    @override
    def parse(self, _, params: list[str]) -> Self | None:
        return self

    @override
    def get_params(self) -> dict[str, Any]:
        pass
