from random import choice
from typing import Self, Any, override

from commands.middleware.global_cooldown import GlobalCooldown
from commands.base_command import BaseCommand

with open("thechaos.txt", "r", encoding="UTF-8") as f:
    thechaos_verses = f.read().split("\n\n")


class TheChaosCommand(BaseCommand):
    name = "thechaos"
    aliases = ["törp"]
    middleware = [GlobalCooldown(5 * 60)]

    @override
    async def execute(self) -> None:
        message = choice(thechaos_verses).replace("\n", " / ")
        await self.chat_message.reply(message)

    @override
    def parse(self, _, params: list[str]) -> Self | None:
        return self

    @override
    def get_params(self) -> dict[str, Any]:
        pass
