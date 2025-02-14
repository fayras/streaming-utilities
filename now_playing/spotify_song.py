import requests

from now_playing.spotify_token import SpotifyToken


class Song:
    def __init__(self, name, artists, progress, duration):
        self.name = name
        self.artists = artists
        self.progress = progress
        self.duration = duration


class SpotifySong:
    def __init__(self):
        self._cache: Song or None = None
        self._update_count = 0
        self._update_interval = 5
        self.token = SpotifyToken.get()

    def _fetch_from_api(self):
        print("Fetching Spotify Song")
        response = requests.get(
            "https://api.spotify.com/v1/me/player/currently-playing",
            headers={"Authorization": f"{self.token.token_type} {self.token.token}"}
        ).json()

        return Song(
            response["item"]["name"],
            ", ".join([a["name"] for a in response["item"]["artists"]]),
            response["progress_ms"],
            response["item"]["duration_ms"]
        )

    def update(self):
        if self._cache is None or self._update_count >= self._update_interval:
            self._cache = self._fetch_from_api()
            self._update_count = 0

        self._update_count += 1

    @property
    def name(self):
        return self._cache.name

    @property
    def artists(self):
        return self._cache.artists

    @property
    def progress(self):
        return self._cache.progress

    @property
    def duration(self):
        return self._cache.duration
