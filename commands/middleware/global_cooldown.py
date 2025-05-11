import os
from datetime import datetime
from typing import Awaitable, Optional, Callable, Dict

from twitchAPI.chat.middleware import BaseCommandMiddleware

from commands import BaseCommand


class GlobalCooldown(BaseCommandMiddleware):
    """Restricts a command to be only executed once every :const:`cooldown_seconds` in any channel"""

    # command -> datetime
    _last_executed: Dict[str, datetime] = {}

    def __init__(self, cooldown_seconds: int):
        """
        :param cooldown_seconds: time in seconds a command should not be used again
        """
        self.execute_blocked_handler = self.on_blocked
        self.cooldown = cooldown_seconds

    @staticmethod
    async def on_blocked(command: 'BaseCommand') -> None:
        username = command.chat_message.user.display_name
        chat_str = command.chat_message.text
        os.system(
            f'notify-send "Command {command.name} noch auf Cooldown" "@{username} {chat_str}"'
        )

    async def can_execute(self, command: BaseCommand) -> bool:
        if self._last_executed.get(command.name) is None:
            return True

        since = (datetime.now() - self._last_executed[
            command.name]).total_seconds()

        return since >= self.cooldown

    async def was_executed(self, command: BaseCommand):
        self._last_executed[command.name] = datetime.now()
