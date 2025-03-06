from typing import override, Self, Any

import twitchAPI.chat

from commands.base_command import BaseCommand, ChatUser
from now_playing.spotify_api import SpotifyAPI


class RequestCommand(BaseCommand):
    name = "request"
    id: str = None
    user: ChatUser = None

    @override
    def execute(self, api: SpotifyAPI) -> (bool, str):
        is_ok, response = api.queue_song(self.id, self.user)
        return is_ok, response

    @override
    def parse(self, params: list[str], user: twitchAPI.chat.ChatUser) -> Self:
        if len(params) > 0:
            self.id = params[0]

        self.user = ChatUser(user.name, user.display_name)

        return self

    @override
    def set_params_from_json(self, params: dict[str, Any]) -> Self | None:
        # {"song_id": "123"}
        if "song_id" in params:
            self.id = params["song_id"]

        if "user" in params:
            self.user = ChatUser.from_dict(params["user"])

        return self

    @override
    def get_params(self) -> dict[str, str]:
        return {
            "song_id": self.id,
            "user": self.user.to_dict(),
        }
