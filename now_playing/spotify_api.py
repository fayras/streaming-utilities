import requests

from now_playing.spotify_token import SpotifyToken


class Song:
    def __init__(self, name, artists, progress, duration):
        self.name = name
        self.artists = artists
        self.progress = progress
        self.duration = duration


class SpotifyAPI:
    def __init__(self):
        self.token = SpotifyToken.get()

    def get_currently_playing(self):
        api_url = "https://api.spotify.com/v1/me/player/currently-playing"
        response = self.do_request(api_url)

        if response.status_code == 200:
            response = response.json()
            if response["currently_playing_type"] == "track":
                return Song(
                    response["item"]["name"],
                    ", ".join([a["name"] for a in response["item"]["artists"]]),
                    response["progress_ms"],
                    response["item"]["duration_ms"]
                )

        return None

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
