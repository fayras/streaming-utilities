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
        response = self.do_request(
            "https://api.spotify.com/v1/me/player/currently-playing")

        if response["currently_playing_type"] == "track":
            return Song(
                response["item"]["name"],
                ", ".join([a["name"] for a in response["item"]["artists"]]),
                response["progress_ms"],
                response["item"]["duration_ms"]
            )

        return None

    def get_headers(self):
        return {
            "Authorization": f"{self.token.token_type} {self.token.token}"
        }

    def do_request(self, url, count=0):
        response = requests.get(
            url=url,
            headers=self.get_headers(),
        )

        if count > 2:
            Exception("do_request called multiple times. " + response.text)

        if response.status_code == 200:
            return response.json()

        if response.status_code == 401:  # 401 = Unauthenticated
            try:
                self.token.refresh()
            except Exception:
                self.token = SpotifyToken.get()

            return self.do_request(url, count + 1)

        raise Exception(
            "Something went wrong while doing request to Spotify. " + response.text)
