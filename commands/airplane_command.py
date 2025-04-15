import random
from typing import Self, Any

from twitchAPI.chat import ChatMessage, ChatUser
from commands.base_command import BaseCommand


class AirplaneCommand(BaseCommand):
    name = "airplane"
    aliases = ["plane"]
    user_cooldown = 15
    user_color: str
    user_name: str

    def execute(self, chat_message: ChatMessage) -> None:
        pass

    def parse(self, _, params: list[str], user: ChatUser) -> Self | None:
        self.user_color = user.color if not user.color is None else (
                    "#%06x" % random.randint(0, 0xFFFFFF))
        self.user_name = user.display_name
        return self

    def set_params_from_json(self, json: dict[str, Any]) -> Self | None:
        return self

    def get_params(self) -> dict[str, Any]:
        return {
            "color": self.user_color,
            "name": self.user_name,
        }
