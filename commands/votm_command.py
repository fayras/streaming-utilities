import argparse
from typing import Self, Any

from twitchAPI.chat import ChatMessage, ChatUser
from commands.base_command import BaseCommand
from db import insert_votm_challenge


class VotmCommand(BaseCommand):
    name = "viewer_of_the_month"
    aliases = ["votm"]
    global_cooldown = 10

    def __init__(self):
        super().__init__()

        self.parser = argparse.ArgumentParser()
        subparsers = self.parser.add_subparsers(dest='action',
                                                help='Action to execute')
        create_parser = subparsers.add_parser("create", help="")
        create_parser.add_argument("description")
        create_parser.add_argument("-m", "--month", type=str)
        status_parser = subparsers.add_parser("status", help="")
        challenge_parse = subparsers.add_parser("challenge", help="")

        self.action = None
        self.description = None
        self.month = None

    # "!votm create DESCRIPTION"
    # "!votm status"
    # "!votm challenge"

    async def execute(self, chat_message: ChatMessage) -> None:
        if self.action == "create":
            insert_votm_challenge(self.month, self.description,
                                  "votm_scripts/test.py")

    def parse(self, _, params: list[str], user: ChatUser) -> Self | None:
        args = self.parser.parse_args(params)
        self.action = args.action

        if args.action == "create" and user.name == "thefayras":
            self.description = args.description
            self.month = (args.month
                          .replace("\"", "")
                          .replace("'", "")) if args.month else ""

        if args.action == "status":
            print("votm status")

        if args.action == "challenge":
            print("votm challenge")

        return self

    def set_params_from_json(self, json: dict[str, Any]) -> Self | None:
        return self

    def get_params(self) -> dict[str, Any]:
        pass
