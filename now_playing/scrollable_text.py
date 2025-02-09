from rich.text import Text

# TODO
class ScrollableText(Text):
    def __init__(self, title, scrollable_text, *args, **kwargs) -> None:
        super().__init__()

    def scroll(self, amount):
        pass