import sys
import requests
import rich
import time

from rich.live import Live
from rich.text import Text
from rich.cells import cell_len
from now_playing.spotify_token import SpotifyToken
from progress_bar import ProgressBar


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


def print_text(label, text, style):
    return f"{label}: [{style}]{rich.markup.escape(text)}[/{style}]\n"


def scroll_text(width, amount, label, text, style):
    if cell_len(label) + cell_len(text) + cell_len(": ") <= width:
        return print_text(label, text, style)

    n = amount % (cell_len(label) + cell_len(text) + cell_len(": ") - width + 2)
    ellipsis = "" if cell_len(label) + cell_len(text) + cell_len(": ") == width + n - 1 else "…"
    available_width = width - cell_len(label) - cell_len(": ") - cell_len(ellipsis)
    text = text[0+n:available_width+n-1].rstrip(" ") + ellipsis
    return print_text(label, text, style)


def show_now_playing():
    token = SpotifyToken.get()

    sys.stdout.write("\x1b[8;{rows};{cols}t".format(rows=4, cols=50))
    console = rich.console.Console(style="on green")
    console.set_window_title("♪♫♪♫♪")
    rich_text = rich.text.Text("")

    elapsed_time = 0
    get_current_song(token)
    progress_bar = ProgressBar()
    with Live(rich_text, auto_refresh=False, console=console) as live:
        live.console.clear()

        rich.print("[green]❯[/green] [blue]./stream[/blue] [cyan]--now-playing[/cyan]")
        while True:
            elapsed_time += 1
            if elapsed_time % 5 == 0:
                get_current_song(token)

            progress_bar.update(live.console, current_song_info["progress"], current_song_info["duration"])
            width = live.console.size.width

            title = scroll_text(width, elapsed_time, "Title", current_song_info["name"], "bold dark_red")
            artist = scroll_text(width, elapsed_time, "Artist", current_song_info["artists"], "bold dark_red")
            rich_text = rich.text.Text.from_markup(title + artist + progress_bar.get())

            live.update(rich_text)
            live.refresh()
            time.sleep(1)