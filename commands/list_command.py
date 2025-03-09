from typing import Self, Any

import twitchAPI.chat
from commands import get_classes_dict
from commands.base_command import BaseCommand, ChatUser


class ListCommand(BaseCommand):
    name = "commands"
    global_cooldown = 120

    async def execute(self,
                      chat_message: twitchAPI.chat.ChatMessage) -> None:
        commands = get_classes_dict()
        commands.pop(self.name)

        commands = map(lambda c: f"!{c}", commands)
        commands_str = "\n".join(commands)
        await chat_message.reply(commands_str)

    def parse(self, params: list[str], user: ChatUser) -> Self | None:
        return self

    def set_params_from_json(self, json: dict[str, Any]) -> Self | None:
        return self

    def get_params(self) -> dict[str, Any]:
        pass
