from abc import ABC, abstractmethod
from typing import Self, Any


class ChatUser:
    name: str
    display_name: str

    def __init__(self, name: str, display_name: str):
        self.name = name
        self.display_name = display_name

    def to_dict(self):
        return {
            "name": self.name,
            "display_name": self.display_name,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]):
        return ChatUser(data["name"], data["display_name"])


class BaseCommand(ABC):
    # class Type(Enum):
    #     CHAT_COMMAND = "CHAT_COMMAND"
    user: ChatUser = None

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    # @property
    # @abstractmethod
    # def type(self) -> Type:
    #     pass

    @abstractmethod
    def execute(self, *args) -> None:
        pass

    @abstractmethod
    def parse(self, params: list[str], user: ChatUser) -> Self | None:
        pass

    @abstractmethod
    def set_params_from_json(self, json: dict[str, Any]) -> Self | None:
        pass

    @abstractmethod
    def get_params(self) -> dict[str, Any]:
        pass

    def to_dict(self) -> dict:
        return {
            "command": self.name,
            "params": self.get_params()
        }
