import random
from typing import Self, Any, override

from twitchAPI.chat import ChatMessage
from commands.base_command import BaseCommand
from commands.middleware.user_cooldown import UserCooldown


class AirplaneCommand(BaseCommand):
    name = "airplane"
    aliases = ["plane"]
    middleware = [UserCooldown(15)]

    def __init__(self,
                 command_string: str,
                 params: list[str],
                 chat_message: ChatMessage
                 ):
        super().__init__(command_string, params, chat_message)
        self.user_color = None
        self.user_name = None

    @override
    def parse(self, _, params: list[str]) -> Self | None:
        user = self.chat_message.user
        self.user_name = user.display_name

        if not user.color is None:
            self.user_color = user.color
        else:
            self.user_color = "#%06x" % random.randint(0, 0xFFFFFF)

        return self

    @override
    def get_params(self) -> dict[str, Any]:
        return {
            "color": self.user_color,
            "name": self.user_name,
        }

    @override
    async def execute(self) -> None:
        pass
