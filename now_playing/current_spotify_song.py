from now_playing.spotify_api import SpotifyAPI, Song


class CurrentSpotifySong:
    def __init__(self, api: SpotifyAPI):
        self.api = api
        self._cache: Song or None = self.api.get_currently_playing()
        self._update_count = 0
        self._update_interval = 5

    def update(self):
        if self._update_count >= self._update_interval:
            self._cache = self.api.get_currently_playing()
            self._update_count = 0

        self._update_count += 1

    def is_track(self):
        return True if self._cache is not None else False

    @property
    def name(self):
        return self._cache.name_with_requested_by

    def set_name(self, name):
        self._cache.name = name

    @property
    def artists(self):
        return self._cache.artists

    @property
    def progress(self):
        return self._cache.progress

    @property
    def duration(self):
        return self._cache.duration
