from typing import Self, Any

import twitchAPI.chat

from commands.base_command import BaseCommand, ChatUser


class CoffeeCommand(BaseCommand):
    name = "coffee"
    user_cooldown = 30
    user_color: str

    def execute(self, chat_message: twitchAPI.chat.ChatMessage) -> None:
        pass

    def parse(self, params: list[str],
              user: twitchAPI.chat.ChatUser) -> Self | None:
        self.user_color = user.color
        return self

    def set_params_from_json(self, json: dict[str, Any]) -> Self | None:
        return self

    def get_params(self) -> dict[str, Any]:
        return {
            "color": self.user_color
        }
