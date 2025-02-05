import math

from rich.console import Console

class ProgressBar:
    current_progress = 0
    total_progress = 0
    character = "#"
    progress_ascii = ""

    def update(self, console: Console, current, total):
        width = console.size.width - 2
        character_count = math.floor(current / total * width)
        self.progress_ascii = "".ljust(character_count, self.character).ljust(width, " ")

    def get(self):
        return f"\\[[bright_black]{self.progress_ascii}[/bright_black]]"