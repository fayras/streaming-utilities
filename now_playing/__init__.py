import asyncio
import json
import os
import threading

import aiohttp
import rich
import time

from rich.live import Live
from rich.text import Text

from now_playing.current_spotify_song import CurrentSpotifySong
from now_playing.scrollable_text import ScrollableText
from now_playing.spotify_api import SpotifyAPI
from now_playing.spotify_token import SpotifyToken
from now_playing.progress_bar import ProgressBar


async def connect_to_websocket(api: SpotifyAPI):
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect('http://localhost:8080/ws') as ws:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    if data["type"] == "CHAT_COMMAND":
                        payload = data["payload"]
                        if payload["command"] == "SONG_REQUEST":
                            is_ok, response = api.queue_song(payload["song_id"])
                            message = "Erfolgreich in Warteschlange aufgenommen." if is_ok else f"Etwas is fehlgeschlagen:\n {response["error"]["message"]}"
                            os.system(
                                f'notify-send "Spotify Request" "{message}"')

                            # TODO: Bei fehlgeschlagenem Request soll der Bot mit
                            # einer Nachricht antworten, dass die ID nicht stimmt
                            # und ggf. bei falscher Benutzung (zB "!request ")
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break


def show_now_playing():
    # sys.stdout.write("\x1b[8;{rows};{cols}t".format(rows=4, cols=50))
    console = rich.console.Console()
    console.set_window_title("♪♫♪♫♪")

    api = SpotifyAPI()
    current_song = CurrentSpotifySong(api)
    title = ScrollableText("Title")
    artist = ScrollableText("Artist")
    progress = ProgressBar()

    # This function will run in the thread
    def run_in_thread():
        loop = asyncio.new_event_loop()
        # Set the loop as the current event loop for this thread
        asyncio.set_event_loop(loop)
        # Run the async function until it completes
        loop.run_until_complete(connect_to_websocket(api))
        # Clean up
        loop.close()

    t = threading.Thread(target=run_in_thread)
    t.daemon = True
    t.start()

    with Live(Text(""), auto_refresh=False, console=console) as live:
        live.console.clear()

        rich.print(
            "[green]❯[/green] [blue]./stream[/blue] [cyan]--now-playing[/cyan]")
        while True:
            width = live.console.size.width

            current_song.update()
            if not current_song.is_track():
                live.update("Currently playing type is not supported.")
            else:
                title.update(current_song.name, width).scroll()
                artist.update(current_song.artists, width).scroll()
                progress.update(live.console, current_song.progress,
                                current_song.duration)
                rich_text = Text.from_markup(f"{title}{artist}{progress}")

                live.update(rich_text)

            live.refresh()
            time.sleep(1)
