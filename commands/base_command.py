import datetime
from abc import ABC, abstractmethod
from typing import Self, Any

from twitchAPI.chat import ChatUser


class BaseCommand(ABC):
    # class Type(Enum):
    #     CHAT_COMMAND = "CHAT_COMMAND"
    user_cooldown: int = -1
    global_cooldown: int = -1
    cooldown = {}

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

    @classmethod
    def check_cooldown(cls, user: ChatUser) -> bool:
        now = datetime.datetime.now()
        cd_key = None
        cooldown = None

        if cls.user_cooldown > -1:
            cd_key = f"{cls.name}_{user.name}"
            cooldown = cls.user_cooldown
        elif cls.global_cooldown > -1:
            cd_key = f"{cls.name}_global"
            cooldown = cls.global_cooldown

        if not cd_key is None:
            current_cooldown = cls.cooldown.get(cd_key)
            if not current_cooldown is None and now <= current_cooldown:
                print(f"is on cooldown for {cd_key}: {current_cooldown}")
                return True

            cls.cooldown[cd_key] = now + datetime.timedelta(seconds=cooldown)

        return False
