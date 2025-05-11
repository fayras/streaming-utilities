from datetime import datetime
from typing import Awaitable, Optional, Callable, Dict

from twitchAPI.chat.middleware import BaseCommandMiddleware

from commands import BaseCommand


class UserCooldown(BaseCommandMiddleware):
    """Restricts a command to be only executed once every :const:`cooldown_seconds` in a channel by a user."""

    # command -> channel -> user -> datetime
    _last_executed: Dict[str, Dict[str, Dict[str, datetime]]] = {}

    def __init__(self,
                 cooldown_seconds: int,
                 execute_blocked_handler: Optional[
                     Callable[[BaseCommand], Awaitable[None]]] = None):
        """
        :param cooldown_seconds: time in seconds a command should not be used again
        :param execute_blocked_handler: optional specific handler for when the execution is blocked
        """
        self.execute_blocked_handler = execute_blocked_handler
        self.cooldown = cooldown_seconds

    async def can_execute(self, command: BaseCommand) -> bool:
        if self._last_executed.get(command.name) is None:
            return True

        room_name = command.chat_message.room.name
        user_name = command.chat_message.user.name
        if self._last_executed[command.name].get(room_name) is None:
            return True

        last_executed = self._last_executed[command.name][room_name].get(
            user_name)

        if last_executed is None:
            return True

        since = (datetime.now() - last_executed).total_seconds()

        return since >= self.cooldown

    async def was_executed(self, command: BaseCommand):
        room_name = command.chat_message.room.name
        user_name = command.chat_message.user.name
        now = datetime.now()

        if self._last_executed.get(command.name) is None:
            self._last_executed[command.name] = {}
            self._last_executed[command.name][room_name] = {}
            self._last_executed[command.name][room_name][user_name] = now
            return

        if self._last_executed[command.name].get(room_name) is None:
            self._last_executed[command.name][room_name] = {}
            self._last_executed[command.name][room_name][user_name] = now
            return

        self._last_executed[command.name][room_name][user_name] = now
