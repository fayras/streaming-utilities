import sys
import requests
import rich
import time

from rich.live import Live
from rich.text import Text
from rich.cells import cell_len
from rich.markup import escape as rich_escape
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


def print_text(label, text, style):
    return f"{label}: [{style}]{rich_escape(text)}[/{style}]\n"


def scroll_text(width, amount, label, text, style):
    total_length = cell_len(label) + cell_len(text) + cell_len(": ")

    # If text fits entirely, no need for scrolling
    if total_length <= width:
        return print_text(label, text, style)

    # Calculate how many positions we need to scroll through
    scroll_length = total_length - width + 2
    scroll_position = amount % (scroll_length + 2)

    # Add pause by repeating the first and last position
    if scroll_position == 0:  # Pause at start
        n = 0
    elif scroll_position == scroll_length + 1:  # Pause at end
        n = scroll_length - 1
    else:  # Normal scrolling
        n = scroll_position - 1

    ellipsis = "" if total_length == width + n - 1 else "…"
    available_width = width - cell_len(label) - cell_len(": ") - cell_len(ellipsis)
    text = text[0 + n:available_width + n - 1].rstrip(" ") + ellipsis
    return print_text(label, text, style)


def show_now_playing():
    token = SpotifyToken.get()

    # sys.stdout.write("\x1b[8;{rows};{cols}t".format(rows=4, cols=50))
    console = rich.console.Console()
    console.set_window_title("♪♫♪♫♪")
    rich_text = Text("")

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
            rich_text = Text.from_markup(title + artist + str(progress_bar))

            live.update(rich_text)
            live.refresh()
            time.sleep(1)