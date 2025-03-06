from enum import Enum
from abc import ABC, abstractmethod
from typing import Self, Any


class BaseCommand(ABC):
    # class Type(Enum):
    #     CHAT_COMMAND = "CHAT_COMMAND"

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
    def parse(self, params: list[str]) -> Self | None:
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
