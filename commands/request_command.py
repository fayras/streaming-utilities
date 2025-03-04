from commands.base_command import BaseCommand


class RequestCommand(BaseCommand):
    name = "request"
    type = BaseCommand.Type.CHAT_COMMAND
    id: str = None

    def __init__(self, song_id):
        self.id = song_id
