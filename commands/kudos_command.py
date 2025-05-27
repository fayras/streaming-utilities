from typing import Self, Any, override

from twitchAPI.chat import ChatMessage
from commands.base_command import BaseCommand
from commands.middleware.user_cooldown import UserCooldown


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

    @override
    async def execute(self) -> None:
        pass

    @override
    def parse(self, _, params: list[str]) -> Self | None:
        if len(params) > 0:
            username = params[0]
            if username.startswith("@"):
                self.twitch_username = username[1:].lower()
            else:
                self.twitch_username = username.lower()

        return self

    @override
    def get_params(self) -> dict[str, Any]:
        pass
