from typing import Self, Any

from twitchAPI.chat import ChatUser, ChatMessage
from commands.base_command import BaseCommand


class CoffeeCommand(BaseCommand):
    name = "coffee"
    aliases = ["tea", "covfefe"]
    user_cooldown = 30
    user_color: str
    type = "coffee"

    def execute(self, chat_message: ChatMessage) -> None:
        pass

    def parse(self, command: str, params: list[str],
              user: ChatUser) -> Self | None:
        self.user_color = user.color
        self.type = command
        return self

    def set_params_from_json(self, json: dict[str, Any]) -> Self | None:
        return self

    def get_params(self) -> dict[str, Any]:
        return {
            "color": self.user_color,
            "type": self.type,
        }
