from typing import Self, Any, override

from commands import get_all_commands
from commands.base_command import BaseCommand
from commands.middleware.global_cooldown import GlobalCooldown


class ListCommand(BaseCommand):
    name = "commands"
    middleware = [GlobalCooldown(120)]

    @override
    async def execute(self) -> None:
        commands = get_all_commands()
        commands.pop(self.name)

        commands = map(lambda c: f"!{c}", commands)
        commands_str = "\n".join(commands)
        await self.chat_message.reply(commands_str)

    @override
    def parse(self, _, params: list[str]) -> Self | None:
        return self

    @override
    def get_params(self) -> dict[str, Any]:
        pass
