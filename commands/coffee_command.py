from typing import Self, Any, override

from twitchAPI.chat import ChatMessage
from commands.base_command import BaseCommand
from commands.middleware.user_cooldown import UserCooldown


class CoffeeCommand(BaseCommand):
    name = "coffee"
    aliases = ["tea", "covfefe"]
    middleware = [UserCooldown(1 * 60)]

    def __init__(
            self,
            command_string: str,
            params: list[str],
            chat_message: ChatMessage
    ):
        super().__init__(command_string, params, chat_message)
        self.user_color = None
        self.type = "coffee"

    @override
    def parse(self, command: str, params: list[str]) -> Self | None:
        self.user_color = self.chat_message.user.color
        self.type = command
        return self

    @override
    def get_params(self) -> dict[str, Any]:
        return {
            "color": self.user_color,
            "type": self.type,
        }

    @override
    async def execute(self) -> None:
        pass
