import io
import os.path
from typing import Self, Any, override

import argparse
from datetime import datetime
from enum import Enum

from twitchAPI.chat import ChatMessage, ChatUser
from commands.base_command import BaseCommand
from commands.middleware.global_cooldown import GlobalCooldown
from db import insert_votm_challenge, get_current_votm_challenge


class VotmCommand(BaseCommand):
    class Action(Enum):
        CREATE = 1
        STATUS = 2
        CHALLENGE = 3

    name = "viewer_of_the_month"
    aliases = ["votm"]
    middleware = [GlobalCooldown(10)]
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

        self.action: VotmCommand.Action | None = None
        self.description = None
        self.month = None
        self.challenge = None

        if VotmCommand.script is None:
            now = datetime.now()
            current_month = f"{now.year}-{now.month:02}"
            script_path = f"votm_scripts/{current_month}.py"
            full_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "..",
                script_path
            )

            if os.path.exists(full_path):
                with open(full_path, mode="r") as script:
                    VotmCommand.script = script.read()

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
            return_value = script_locals["return_value"]
            await self.chat_message.reply(
                f"Aktueller Stand: {return_value}"
            )

    @override
    def parse(self, _, params: list[str]) -> Self | None:
        if len(params) == 0:
            self.action = VotmCommand.Action.CHALLENGE
            return self

        args = self.parser.parse_args(params)

        user = self.chat_message.user
        if user.name == "thefayras" and args.action == "create":
            self.action = VotmCommand.Action.CREATE
            self.description = args.description
            self.month = args.month if args.month else ""

        if args.action == "status":
            self.action = VotmCommand.Action.STATUS

        if args.action == "challenge":
            self.action = VotmCommand.Action.CHALLENGE

        return self

    @override
    def get_params(self) -> dict[str, Any]:
        pass
