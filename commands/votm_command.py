import io
import os.path
from typing import Self, Any, override

import argparse
from datetime import datetime
from enum import Enum

from dateutil.relativedelta import relativedelta
from twitchAPI.chat import ChatMessage, ChatUser
from twitchAPI.helper import first
from commands.base_command import BaseCommand
from commands.middleware.global_cooldown import GlobalCooldown
from commands.middleware.streamer_only import StreamerOnly
from db import insert_votm_challenge, get_current_votm_challenge, \
    insert_votm_winner


class VotmMiddleware(StreamerOnly):
    async def can_execute(self, command: 'VotmCommand') -> bool:
        if (command.action is VotmCommand.Action.CREATE
                or command.action is VotmCommand.Action.WINNER):
            return await super().can_execute(command)

        return True


class VotmCommand(BaseCommand):
    class Action(Enum):
        CREATE = 1
        STATUS = 2
        CHALLENGE = 3
        WINNER = 4

    name = "viewer_of_the_month"
    aliases = ["votm"]
    middleware = [GlobalCooldown(10), VotmMiddleware()]
    script = None

    def __init__(
            self,
            command_string: str,
            params: list[str],
            chat_message: ChatMessage
    ):
        super().__init__(command_string, params, chat_message)

        self.parser = argparse.ArgumentParser()
        subparsers = self.parser.add_subparsers(dest='action',
                                                help='Aktion, die ausgeführt werden soll.')
        create_parser = subparsers.add_parser("create",
                                              help="Erzeugt eine neue Challenge. (Nur Admins & Mods)")
        create_parser.add_argument("description",
                                   help="Die Beschreibung der Challenge.")
        create_parser.add_argument("-m", "--month", type=str,
                                   help="Der Monat, der Challenge im Format 'YYYY-MM'.")
        status_parser = subparsers.add_parser("status",
                                              help="Zeige den Status der aktuellen Challenge an.")
        challenge_parse = subparsers.add_parser("challenge",
                                                help="Zeige die aktuelle Challenge an.")
        winner_parse = subparsers.add_parser("winner", help="")

        self.action: VotmCommand.Action | None = None
        self.description = None
        self.month = None
        self.challenge = None

        if VotmCommand.script is None:
            VotmCommand.script = VotmCommand.load_script()

    @staticmethod
    def get_month(month_delta=0):
        date = datetime.now() + relativedelta(months=month_delta)
        return f"{date.year}-{date.month:02}"

    @staticmethod
    def load_script(month_delta=0):
        current_month = VotmCommand.get_month(month_delta)
        script_path = f"votm_scripts/{current_month}.py"
        full_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            script_path
        )

        if os.path.exists(full_path):
            with open(full_path, mode="r") as script:
                return script.read()

        return ""

    @override
    async def execute(self) -> None:
        if self.action is None:
            # TODO: Help Nachricht schöner für den Twitch Chat formatieren
            help_buffer = io.StringIO()
            self.parser.print_help(help_buffer)
            help_text = help_buffer.getvalue()
            help_buffer.close()
            await self.chat_message.reply(help_text)

        if self.action == VotmCommand.Action.CREATE:
            script_path = f"votm_scripts/{self.month}.py"
            full_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "..",
                script_path
            )

            if not os.path.exists(full_path):
                with open(full_path, "w") as f:
                    content = (
                        f"# Das Skript für die Challenge des Monats {self.month}.\n#\n"
                        f"# Die Challenge des Monats ist:\n"
                        f"# {self.description}\n\n"
                    )
                    f.write(content)

            insert_votm_challenge(self.month, self.description,
                                  script_path)

        if self.action == VotmCommand.Action.CHALLENGE:
            self.challenge = get_current_votm_challenge()
            await self.chat_message.reply(
                f"Die Challenge des Monats ist: {self.challenge}"
            )

        if self.action == VotmCommand.Action.STATUS:
            script_locals = {}
            exec(VotmCommand.script, None, script_locals)
            chat_message, _ = script_locals["return_value"]
            await self.chat_message.reply(
                f"Aktueller Stand: {chat_message}"
            )

        if self.action == VotmCommand.Action.WINNER:
            script = VotmCommand.load_script(-1)
            script_locals = {}
            exec(script, None, script_locals)
            _, ids = script_locals["return_value"]
            if len(ids) > 0:
                user_id = ids[0]
                api = self.chat_message.chat.twitch
                user = await first(api.get_users(logins=[user_id]))
                profile_img = user.profile_image_url
                month = VotmCommand.get_month(-1)
                insert_votm_winner(month, user_id, profile_img)

    @override
    def parse(self, _, params: list[str]) -> Self | None:
        if len(params) == 0:
            self.action = VotmCommand.Action.CHALLENGE
            return self

        args = self.parser.parse_args(params)

        if args.action == "create":
            self.action = VotmCommand.Action.CREATE
            self.description = args.description
            self.month = args.month if args.month else ""

        if args.action == "status":
            self.action = VotmCommand.Action.STATUS

        if args.action == "challenge":
            self.action = VotmCommand.Action.CHALLENGE

        if args.action == "winner":
            self.action = VotmCommand.Action.WINNER

        return self

    @override
    def get_params(self) -> dict[str, Any]:
        pass
