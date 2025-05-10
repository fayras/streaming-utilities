from typing import Self, Any, override

from twitchAPI.chat import ChatMessage, ChatUser
from twitchAPI.helper import first
from commands.base_command import BaseCommand
from commands.middleware.streamer_only import StreamerOnly


class ShoutoutCommand(BaseCommand):
    name = "shoutout"
    aliases = ["so"]
    middleware = [StreamerOnly()]

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
        req = self.chat_message.chat.twitch.get_users(
            logins=[self.twitch_username])
        user = await first(req)
        print(user)

    @override
    def parse(self, _, params: list[str]) -> Self | None:
        if len(params) > 0:
            username = params[0]
            if username.startswith("@"):
                self.twitch_username = username[1:]
            else:
                self.twitch_username = username

        return self

    @override
    def get_params(self) -> dict[str, Any]:
        pass
