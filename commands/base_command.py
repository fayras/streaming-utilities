from enum import Enum


class BaseCommand:
    class Type(Enum):
        CHAT_COMMAND = "CHAT_COMMAND"

    name: str
    type: Type
