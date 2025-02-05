import sys
import requests
import rich
import webbrowser
import time

from rich.live import Live
from dotenv import dotenv_values
from urllib.parse import urlencode
from http.server import HTTPServer

from progress_bar import ProgressBar
from server import Server


def get_current_song(token):
    now_playing_response = requests.get(
        "https://api.spotify.com/v1/me/player/currently-playing",
        headers={"Authorization": f"{token.token_type} {token.token}"}
    ).json()

    return {
        "name": now_playing_response["item"]["name"],
        "artists": " ".join([a["name"] for a in now_playing_response["item"]["artists"]]),
        "progress": now_playing_response["progress_ms"],
        "duration": now_playing_response["item"]["duration_ms"],
    }


def show_now_playing():
    env_values = dotenv_values(".env")
    params = urlencode({
        "response_type": "code",
        "scope": "user-read-currently-playing",
        "redirect_uri": env_values["REDIRECT_URI"],
        "client_id": env_values["CLIENT_ID"],
    })

    webbrowser.open("https://accounts.spotify.com/authorize?" + params)
    handler = Server
    server = HTTPServer(("localhost", 8989), handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        pass

    token = server.access_token

    sys.stdout.write("\x1b[8;{rows};{cols}t".format(rows=4, cols=50))
    console = rich.console.Console(style="on green")
    console.set_window_title("Now Playing")
    rich_text = rich.text.Text("")
    progress_bar = ProgressBar()
    with Live(rich_text, auto_refresh=False, console=console) as live:
        live.console.clear()

        rich.print("[green]❯[/green] [blue]./stream[/blue] [cyan]--now-playing[/cyan]")
        while True:
            current_song = get_current_song(token)
            progress_bar.update(live.console, current_song["progress"], current_song["duration"])

            rich_text = rich.text.Text.from_markup(
                f"Title: [bold dark_red]{rich.markup.escape(current_song["name"])}[/bold dark_red]\n"
                f"Artist: [bold dark_red]{rich.markup.escape(current_song["artists"])}[/bold dark_red]"
                f"\n{progress_bar.get()}")

            live.update(rich_text)
            live.refresh()
            time.sleep(3)