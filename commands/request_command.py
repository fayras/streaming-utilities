from typing import override, Self, Any

from commands.base_command import BaseCommand
from now_playing.spotify_api import SpotifyAPI


class RequestCommand(BaseCommand):
    name = "request"
    id: str = None

    @override
    def execute(self, api: SpotifyAPI) -> (bool, str):
        is_ok, response = api.queue_song(self.id)
        return is_ok, response

    @override
    def parse(self, params: list[str]) -> Self:
        if len(params) > 0:
            self.id = params[0]

        return self

    @override
    def set_params_from_json(self, params: dict[str, Any]) -> Self | None:
        # {"song_id": "123"}
        if "song_id" in params:
            self.id = params["song_id"]

        return self

    @override
    def get_params(self) -> dict[str, str]:
        return {
            "song_id": self.id,
        }
