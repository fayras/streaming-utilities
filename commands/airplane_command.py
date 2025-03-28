from typing import Self, Any

import twitchAPI.chat

from commands.base_command import BaseCommand, ChatUser


class AirplaneCommand(BaseCommand):
    name = "airplane"
    user_cooldown = 15
    user_color: str
    user_name: str

    def execute(self, chat_message: twitchAPI.chat.ChatMessage) -> None:
        pass

    def parse(self, params: list[str],
              user: twitchAPI.chat.ChatUser) -> Self | None:
        self.user_color = user.color
        self.user_name = user.display_name
        return self

    def set_params_from_json(self, json: dict[str, Any]) -> Self | None:
        return self

    def get_params(self) -> dict[str, Any]:
        return {
            "color": self.user_color,
            "name": self.user_name,
        }
