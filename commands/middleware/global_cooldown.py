from datetime import datetime
from typing import Awaitable, Optional, Callable, Dict

from twitchAPI.chat.middleware import BaseCommandMiddleware

from commands import BaseCommand


class GlobalCooldown(BaseCommandMiddleware):
    """Restricts a command to be only executed once every :const:`cooldown_seconds` in any channel"""

    # command -> datetime
    _last_executed: Dict[str, datetime] = {}

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

    def can_execute(self, command: BaseCommand) -> bool:
        if self._last_executed.get(command.name) is None:
            return True

        since = (datetime.now() - self._last_executed[
            command.name]).total_seconds()

        return since >= self.cooldown

    def was_executed(self, command: BaseCommand):
        self._last_executed[command.name] = datetime.now()
