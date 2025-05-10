import datetime
from abc import ABC, abstractmethod
from typing import Self, Any

from twitchAPI.chat import ChatUser, ChatMessage
from twitchAPI.chat.middleware import BaseCommandMiddleware


class BaseCommand(ABC):
    # class Type(Enum):
    #     CHAT_COMMAND = "CHAT_COMMAND"
    # user_cooldown: int = -1
    # global_cooldown: int = -1
    # cooldown = {}
    aliases = []
    middleware: list[BaseCommandMiddleware] = []

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    # @property
    # @abstractmethod
    # def type(self) -> Type:
    #     pass

    def __init__(
            self,
            command_string: str,
            params: list[str],
            chat_message: ChatMessage
    ):
        self.chat_message = chat_message
        self.parse(command_string, params)

    @abstractmethod
    def parse(self, command: str, params: list[str]) -> Self | None:
        pass

    @abstractmethod
    async def execute(self) -> None:
        pass

    @abstractmethod
    def get_params(self) -> dict[str, Any]:
        pass

    def run(self):
        for middleware in self.middleware:
            if not middleware.can_execute(self):
                return

        self.execute()

        for middleware in self.middleware:
            middleware.was_executed(self)

    def to_dict(self) -> dict:
        return {
            "command": self.name,
            "params": self.get_params()
        }

    # @classmethod
    # def check_cooldown(cls, user: ChatUser) -> bool:
    #     now = datetime.datetime.now()
    #     cd_key = None
    #     cooldown = None
    #
    #     if cls.user_cooldown > -1:
    #         cd_key = f"{cls.name}_{user.name}"
    #         cooldown = cls.user_cooldown
    #     elif cls.global_cooldown > -1:
    #         cd_key = f"{cls.name}_global"
    #         cooldown = cls.global_cooldown
    #
    #     if not cd_key is None:
    #         current_cooldown = cls.cooldown.get(cd_key)
    #         if not current_cooldown is None and now <= current_cooldown:
    #             print(f"is on cooldown for {cd_key}: {current_cooldown}")
    #             return True
    #
    #         cls.cooldown[cd_key] = now + datetime.timedelta(seconds=cooldown)
    #
    #     return False
