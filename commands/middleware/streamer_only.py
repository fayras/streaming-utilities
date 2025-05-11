from typing import Awaitable, Optional, Callable

from twitchAPI.chat.middleware import BaseCommandMiddleware

from commands import BaseCommand


class StreamerOnly(BaseCommandMiddleware):
    """Restricts the use of commands to only the streamer in their channel"""

    def __init__(self, execute_blocked_handler: Optional[
        Callable[[BaseCommand], Awaitable[None]]] = None):
        """
        :param execute_blocked_handler: optional specific handler for when the execution is blocked
        """
        self.execute_blocked_handler = execute_blocked_handler

    async def can_execute(self, command: BaseCommand) -> bool:
        msg = command.chat_message
        return msg.room.name == msg.user.name

    async def was_executed(self, command: BaseCommand):
        pass
