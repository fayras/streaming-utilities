import requests

from commands.base_command import ChatUser
from now_playing.spotify_token import SpotifyToken


class Song:
    def __init__(self, name, artists, progress, duration, requested_by=None):
        self.name = name
        self.artists = artists
        self.progress = progress
        self.duration = duration
        self.requested_by = requested_by

    @property
    def name_with_requested_by(self):
        if self.requested_by:
            return f"{self.name} (Wunsch von {self.requested_by.display_name})"

        return self.name


class SpotifyAPI:
    token: SpotifyToken
    # TODO: Ggf sollte "song_requests" aufgeräumt werden. Zb wenn der gewünschte
    #       Song endet, sollte das id-user Paar entfernt werden.
    song_requests: dict[str, ChatUser]

    def __init__(self):
        self.token = SpotifyToken.get()
        self.song_requests = {}

    def get_currently_playing(self):
        api_url = "https://api.spotify.com/v1/me/player/currently-playing"
        response = self.do_request(api_url)

        if response.status_code == 200:
            response = response.json()
            if response["currently_playing_type"] == "track":
                id = response["item"]["id"]
                requested_by = self.song_requests.get(id)
                return Song(
                    response["item"]["name"],
                    ", ".join([a["name"] for a in response["item"]["artists"]]),
                    response["progress_ms"],
                    response["item"]["duration_ms"],
                    requested_by
                )

        return None

    def queue_song(self, id: str, user: ChatUser):
        full_id = f"spotify:track:{id}"
        api_url = "https://api.spotify.com/v1/me/player/queue"

        # TODO: Vorher überprüfen, ob es sich bei der ID um einen echten Track
        #       handelt. Da bei einer ID eines Albums trotzdem 200 OK zurück-
        #       gegeben wird. (Siehe https://api.spotify.com/v1/tracks/{id})
        response = self.do_request(api_url, requests.post, {"uri": full_id})

        if not response.status_code == 200:
            return False, response.json()

        self.song_requests[id] = user
        return True, "OK"

    def get_headers(self):
        return {"Authorization": f"{self.token.token_type} {self.token.token}"}

    def check_token(self):
        if not self.token.is_valid():
            try:
                self.token.refresh()
            except Exception:
                self.token = SpotifyToken.get()

    def do_request(self, url, method=requests.get, params=None):
        self.check_token()

        if params is None:
            params = {}

        return method(url=url, params=params, headers=self.get_headers())
