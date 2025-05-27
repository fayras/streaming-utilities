import os
from datetime import datetime, timedelta
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

    async def on_blocked(self, command: 'BaseCommand') -> None:
        last_executed = self._last_executed.get(command.name)
        date = last_executed + timedelta(seconds=self.cooldown)
        message = (f"Command \"{command.name}\" noch auf Cooldown. "
                   f"Ihr könnt ihn ab {date.strftime("%H:%M:%S")} wieder benutzen.")

        await command.chat_message.reply(message)

    async def can_execute(self, command: BaseCommand) -> bool:
        if self._last_executed.get(command.name) is None:
            return True

        since = (datetime.now() - self._last_executed[
            command.name]).total_seconds()

        return since >= self.cooldown

    async def was_executed(self, command: BaseCommand):
        self._last_executed[command.name] = datetime.now()
