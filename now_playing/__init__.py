import asyncio
import json
import os
import threading
from functools import partial

import rich
import time

from rich.live import Live
from rich.text import Text

from common.WebsocketClient import WebSocketClient
from now_playing.current_spotify_song import CurrentSpotifySong
from now_playing.scrollable_text import ScrollableText
from now_playing.spotify_api import SpotifyAPI
from now_playing.spotify_token import SpotifyToken
from now_playing.progress_bar import ProgressBar


async def parse_and_run_command(api: SpotifyAPI, data: str):
    try:
        parsed_json = json.loads(data)
        command = parsed_json.get("command")
        if command == "request":
            params = parsed_json.get("params")
            song_id = params["song_id"]
            user_name = params["user_name"]
            is_ok, error = api.queue_song(song_id, user_name)
            # is_ok, error = command.execute(api)
            success_message = "Erfolgreich in Warteschlange aufgenommen."
            error_message = f"Etwas is fehlgeschlagen:\n {error}"
            message = success_message if is_ok else error_message
            os.system(f'notify-send "Spotify Request" "{message}"')
    except:
        print("Not valid JSON")


async def connect_to_websocket(ws_client: WebSocketClient):
    await ws_client.start()
    print("websocket client end")


def show_now_playing():
    # sys.stdout.write("\x1b[8;{rows};{cols}t".format(rows=4, cols=50))
    console = rich.console.Console()
    console.set_window_title("♪♫♪♫♪")

    api = SpotifyAPI()
    current_song = CurrentSpotifySong(api)
    title = ScrollableText("Title")
    artist = ScrollableText("Artist")
    progress = ProgressBar()

    websocket_handler = partial(parse_and_run_command, api)
    websocket_client = WebSocketClient("now_playing", websocket_handler)

    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(connect_to_websocket(websocket_client))
        loop.close()

    t = threading.Thread(target=run_in_thread)
    t.daemon = True
    t.start()

    with Live(Text(""), auto_refresh=False, console=console) as live:
        live.console.clear()

        old_websocket_connected = None
        cli_command = "[green]❯[/green] [blue]./stream[/blue] [cyan]--now-playing[/cyan]"
        while True:
            websocket_connected = websocket_client.is_connected()
            has_just_connected = websocket_connected and not old_websocket_connected
            old_websocket_connected = websocket_client.is_connected()
            cli_status = "" if websocket_connected else "[red](Disconnected)[/red]"

            if has_just_connected:
                live.console.clear()

            current_song.update()
            if not current_song.is_track():
                live.update("Currently playing type is not supported.")
            else:
                width = live.console.size.width
                title.update(current_song.name, width).scroll()
                artist.update(current_song.artists, width).scroll()
                progress.update(live.console, current_song.progress,
                                current_song.duration)
                rich_text = Text.from_markup(
                    f"{cli_status}{cli_command}\n{title}{artist}{progress}")

                live.update(rich_text)

            live.refresh()
            time.sleep(1)
