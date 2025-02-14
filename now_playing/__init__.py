import requests
import rich
import time

from rich.live import Live
from rich.text import Text

from now_playing.scrollable_text import ScrollableText
from now_playing.spotify_token import SpotifyToken
from now_playing.progress_bar import ProgressBar


current_song_info = {}


def get_current_song(token):
    now_playing_response = requests.get(
        "https://api.spotify.com/v1/me/player/currently-playing",
        headers={"Authorization": f"{token.token_type} {token.token}"}
    ).json()

    current_song_info["name"] = now_playing_response["item"]["name"]
    current_song_info["artists"] = ", ".join([a["name"] for a in now_playing_response["item"]["artists"]])
    current_song_info["progress"] = now_playing_response["progress_ms"]
    current_song_info["duration"] = now_playing_response["item"]["duration_ms"]


def show_now_playing():
    token = SpotifyToken.get()

    # sys.stdout.write("\x1b[8;{rows};{cols}t".format(rows=4, cols=50))
    console = rich.console.Console()
    console.set_window_title("♪♫♪♫♪")

    elapsed_time = 0
    get_current_song(token)
    title = ScrollableText("Title")
    artist = ScrollableText("Artist")
    progress = ProgressBar()
    with Live(Text(""), auto_refresh=False, console=console) as live:
        live.console.clear()

        rich.print("[green]❯[/green] [blue]./stream[/blue] [cyan]--now-playing[/cyan]")
        while True:
            elapsed_time += 1
            if elapsed_time % 5 == 0:
                get_current_song(token)

            width = live.console.size.width
            title.update(current_song_info["name"], width).scroll()
            artist.update(current_song_info["artists"], width).scroll()
            progress.update(live.console, current_song_info["progress"], current_song_info["duration"])
            rich_text = Text.from_markup(f"{title}{artist}{progress}")

            live.update(rich_text)
            live.refresh()
            time.sleep(1)