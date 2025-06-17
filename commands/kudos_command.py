import random
from typing import Self, Any, override

from twitchAPI.chat import ChatMessage
from commands.base_command import BaseCommand
from commands.middleware.user_cooldown import UserCooldown
from db import get_user_by_username

with open("kudos.txt", "r", encoding="UTF-8") as f:
    kudos_messages = f.read().splitlines()


class KudosCommand(BaseCommand):
    name = "kudos"
    middleware = [UserCooldown(15)]

    def __init__(
            self,
            command_string: str,
            params: list[str],
            chat_message: ChatMessage
    ):
        super().__init__(command_string, params, chat_message)
        self.twitch_username = None
        self.twitch_displayname = None

    @override
    async def execute(self) -> None:
        kudos_message: str = random.choice(kudos_messages)
        reply_message = kudos_message.replace(
            "<X>",
            self.twitch_displayname or self.twitch_username
        )
        await self.chat_message.reply(reply_message)

    @override
    def parse(self, _, params: list[str]) -> Self | None:
        if len(params) > 0:
            username = params[0]
            if username.startswith("@"):
                self.twitch_username = username[1:].lower()
            else:
                self.twitch_username = username.lower()

            user = get_user_by_username(self.twitch_username)
            self.twitch_displayname = user[2] if user is not None else None

        return self

    @override
    def get_params(self) -> dict[str, Any]:
        return {
            "recipient": self.twitch_username,
        }
