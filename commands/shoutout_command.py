from typing import Self, Any, override

from twitchAPI.chat import ChatMessage
from commands.base_command import BaseCommand
from commands.middleware.global_cooldown import GlobalCooldown
from commands.middleware.streamer_only import StreamerOnly


class ShoutoutCommand(BaseCommand):
    name = "shoutout"
    aliases = ["so"]
    middleware = [StreamerOnly(), GlobalCooldown(120)]

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
        tw = self.chat_message.chat.twitch
        req = tw.get_users(
            logins=[self.chat_message.user.name, self.twitch_username])
        from_user = await anext(req)
        to_user = await anext(req)

        channel_url = f"https://twitch.tv/{to_user.login}"
        await self.chat_message.chat.send_message(
            self.chat_message.room,
            f"Dies ist eine sehr coole Person, schaut mal hier vorbei: {channel_url} !"
        )
        await tw.send_a_shoutout(from_user.id, to_user.id, from_user.id)

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
