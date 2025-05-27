import os
from datetime import datetime, timedelta
from typing import Awaitable, Optional, Callable, Dict

from twitchAPI.chat.middleware import BaseCommandMiddleware

from commands import BaseCommand


class UserCooldown(BaseCommandMiddleware):
    """Restricts a command to be only executed once every :const:`cooldown_seconds` in a channel by a user."""

    # command -> channel -> user -> datetime
    _last_executed: Dict[str, Dict[str, Dict[str, datetime]]] = {}

    def __init__(self, cooldown_seconds: int):
        """
        :param cooldown_seconds: time in seconds a command should not be used again
        """
        self.execute_blocked_handler = self.on_blocked
        self.cooldown = cooldown_seconds

    async def on_blocked(self, command: 'BaseCommand') -> None:
        username = command.chat_message.user.name
        room_name = command.chat_message.room.name

        last_executed = self._last_executed[command.name][room_name].get(
            username)

        date = last_executed + timedelta(seconds=self.cooldown)
        message = (f"Command \"{command.name}\" noch auf Cooldown. "
                   f"Du kannst ihn ab {date.strftime("%H:%M:%S")} wieder benutzen.")
        api = command.chat_message.chat.twitch
        if room_name == username:
            req = api.get_users(logins=[username])
            from_user = await anext(req)
            to_user = from_user
        else:
            req = api.get_users(logins=[room_name, username])
            from_user = await anext(req)
            to_user = await anext(req)

        await api.send_whisper(from_user.id, to_user.id, message)

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
