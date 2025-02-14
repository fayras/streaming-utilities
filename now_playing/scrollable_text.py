from rich.cells import cell_len
from rich.markup import escape as rich_escape


class ScrollableText:
    def __init__(self, title, scrollable_text = "", width = 0, style = "bold dark_red") -> None:
        self.title = title
        self.seperator = ": " if title != "" else ""
        self.scrollable_text = scrollable_text
        self.current_text = scrollable_text
        self.width = width
        self.style = style
        self.offset = 0

    def scroll(self, amount = 1):
        title_len = cell_len(self.title)
        text_len = cell_len(self.scrollable_text)
        seperator_len = cell_len(self.seperator)

        total_length = title_len + text_len + seperator_len

        # If text fits entirely, no need for scrolling
        if total_length <= self.width:
            return

        # Calculate how many positions we need to scroll through
        scroll_length = total_length - self.width + 2
        scroll_position = self.offset % (scroll_length + 2)
        self.offset += amount

        # Add pause by repeating the first and last position
        if scroll_position == 0:  # Pause at start
            n = 0
        elif scroll_position == scroll_length + 1:  # Pause at end
            n = scroll_length - 1
        else:  # Normal scrolling
            n = scroll_position - 1

        ellipsis = "" if total_length == self.width + n - 1 else "…"
        available_width = self.width - title_len - seperator_len - cell_len(ellipsis)
        self.current_text = self.scrollable_text[0 + n:available_width + n - 1].rstrip(" ") + ellipsis

    def update_text(self, text):
        if self.scrollable_text != text:
            self.offset = 0

        self.scrollable_text = text
        self.current_text = text

    def update_width(self, width):
        self.width = width

    def update(self, text, width):
        self.update_text(text)
        self.update_width(width)
        return self

    def __str__(self):
        return f"{self.title}: [{self.style}]{rich_escape(self.current_text)}[/{self.style}]\n"

