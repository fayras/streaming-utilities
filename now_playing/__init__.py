import rich
import time

from rich.live import Live
from rich.text import Text

from now_playing.current_spotify_song import CurrentSpotifySong
from now_playing.scrollable_text import ScrollableText
from now_playing.spotify_token import SpotifyToken
from now_playing.progress_bar import ProgressBar


def show_now_playing():
    # sys.stdout.write("\x1b[8;{rows};{cols}t".format(rows=4, cols=50))
    console = rich.console.Console()
    console.set_window_title("♪♫♪♫♪")

    current_song = CurrentSpotifySong()
    title = ScrollableText("Title")
    artist = ScrollableText("Artist")
    progress = ProgressBar()
    with Live(Text(""), auto_refresh=False, console=console) as live:
        live.console.clear()

        rich.print("[green]❯[/green] [blue]./stream[/blue] [cyan]--now-playing[/cyan]")
        while True:
            width = live.console.size.width

            current_song.update()
            title.update(current_song.name, width).scroll()
            artist.update(current_song.artists, width).scroll()
            progress.update(live.console, current_song.progress, current_song.duration)
            rich_text = Text.from_markup(f"{title}{artist}{progress}")

            live.update(rich_text)
            live.refresh()
            time.sleep(1)