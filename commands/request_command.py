from typing import override, Self, Any

from twitchAPI.chat import ChatUser

from commands.base_command import BaseCommand
from now_playing.spotify_api import SpotifyAPI


class RequestCommand(BaseCommand):
    name = "request"
    id: str = None
    user_name: str = None
    user_cooldown = 60

    @override
    def execute(self, api: SpotifyAPI) -> (bool, str):
        is_ok, response = api.queue_song(self.id, self.user_name)
        return is_ok, response

    @override
    def parse(self, params: list[str], user: ChatUser) -> Self:
        if len(params) > 0:
            self.id = params[0]

        self.user_name = user.display_name

        return self

    @override
    def set_params_from_json(self, params: dict[str, Any]) -> Self | None:
        # {"song_id": "123"}
        if "song_id" in params:
            self.id = params["song_id"]

        if "user_name" in params:
            self.user_name = params["user_name"]

        return self

    @override
    def get_params(self) -> dict[str, str]:
        return {
            "song_id": self.id,
            "user_name": self.user_name,
        }
