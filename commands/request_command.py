from typing import override, Self

from twitchAPI.chat import ChatMessage

from commands.base_command import BaseCommand
from commands.middleware.user_cooldown import UserCooldown


class RequestCommand(BaseCommand):
    name = "request"
    middleware = [UserCooldown(30)]

    def __init__(self, command_string: str, params: list[str],
                 chat_message: ChatMessage):
        super().__init__(command_string, params, chat_message)
        self.id = None
        self.user_name = None

    @override
    async def execute(self) -> None:
        pass

    @override
    def parse(self, _, params: list[str]) -> Self:
        if len(params) > 0:
            self.id = params[0]

        self.user_name = self.chat_message.user.display_name

        return self

    @override
    def get_params(self) -> dict[str, str]:
        return {
            "song_id": self.id,
            "user_name": self.user_name,
        }
