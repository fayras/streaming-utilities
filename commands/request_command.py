from typing import override, Self, Any

from twitchAPI.chat import ChatUser, ChatMessage

from commands.base_command import BaseCommand


class RequestCommand(BaseCommand):
    name = "request"
    id: str = None
    user_name: str = None
    user_cooldown = 60

    @override
    async def execute(self, chat_message: ChatMessage) -> None:
        pass

    @override
    def parse(self, _, params: list[str], user: ChatUser) -> Self:
        if len(params) > 0:
            self.id = params[0]

        self.user_name = user.display_name

        return self

    @override
    def get_params(self) -> dict[str, str]:
        return {
            "song_id": self.id,
            "user_name": self.user_name,
        }
