import datetime
import json
import os
import random
import re

import argparse
import sqlite3
import inspect

from importlib.util import spec_from_file_location, module_from_spec
from sqlite3 import Connection

import twitchAPI.chat

from commands import BaseCommand
from config import config
from database.DatabaseMigration import DatabaseMigration


def connect_db(path=config.database_path):
    connection = sqlite3.connect(
        path,
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
    )
    connection.row_factory = sqlite3.Row

    return connection


def get_script_version(path):
    version = path.split('_')[0]
    return int(version)


def get_all_migration_versions():
    _, files = get_migration_files()
    return [get_script_version(file) for file in files]


def get_migration_files():
    directory = os.path.dirname(__file__)
    migrations_path = os.path.join(directory, 'database/migrations/')
    migration_files = [file for file in list(os.listdir(migrations_path)) if
                       not file.startswith("__")]
    return migrations_path, migration_files


def get_migration_module(migrations_path, migration_file):
    full_path = os.path.join(migrations_path, migration_file)
    spec = spec_from_file_location(migration_file[:-3], full_path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def get_migration_from_module(module):
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if (not issubclass(obj, DatabaseMigration)
                or obj == DatabaseMigration):
            continue

        return obj()


def is_current_version(db: Connection):
    current_version = db.cursor().execute('pragma user_version').fetchone()[0]
    max_version = max(get_all_migration_versions())

    return max_version == current_version


def migrate_db(db: Connection):
    current_version = db.cursor().execute('pragma user_version').fetchone()[0]
    migrations_path, migration_files = get_migration_files()
    for migration_file in sorted(migration_files):
        migration_version = get_script_version(migration_file)
        if migration_version <= current_version:
            continue

        module = get_migration_module(migrations_path, migration_file)
        migration: DatabaseMigration = get_migration_from_module(module)
        migration.up(db)

        db.cursor().execute(f"PRAGMA user_version={migration_version}")
        db.commit()


def downgrade_db(db: Connection, to_version=0):
    current_version = db.cursor().execute('pragma user_version').fetchone()[0]
    migrations_path, migration_files = get_migration_files()
    for migration_file in sorted(migration_files, reverse=True):
        migration_version = get_script_version(migration_file)
        if migration_version > current_version:
            continue

        if migration_version == to_version:
            break

        module = get_migration_module(migrations_path, migration_file)
        migration: DatabaseMigration = get_migration_from_module(module)
        migration.down(db)

        db.cursor().execute(f"PRAGMA user_version={migration_version - 1}")
        db.commit()


def get_migration_template(name_snake_case):
    name = "".join(x.capitalize() for x in name_snake_case.lower().split("_"))

    return f"""from sqlite3 import Connection
from database.DatabaseMigration import DatabaseMigration\n\n
class {name}(DatabaseMigration):
    def up(self, connection: Connection) -> None:
        pass

    def down(self, connection: Connection) -> None:
        pass
    """


def create_migration(name):
    template = get_migration_template(name)
    versions = get_all_migration_versions()
    max_version = max(versions)

    directory = os.path.dirname(__file__)
    migrations_path = os.path.join(directory, 'database/migrations/')
    file_name = f"{max_version + 1:04}_{name}.py"
    with open(os.path.join(migrations_path, file_name), "w") as f:
        f.write(template)


def query(query: str, parameters=None):
    with sqlite3.connect(config.database_path) as connection:
        db_cursor = connection.cursor()
        result = db_cursor.execute(query, parameters).fetchall()
        connection.commit()
        db_cursor.close()

    return result


def get_current_votm_challenge():
    now = datetime.datetime.now()
    current_month = f"{now.year}-{now.month:02}"
    result = query(
        "SELECT description FROM viewer_of_the_month_challenges where month = ?",
        (current_month,)
    )

    if len(result) == 0:
        raise Exception("Challenge for current month missing.")

    return result[0][0]


def insert_votm_challenge(month: str, description: str, script_path: str):
    if re.match(r"\d{4}-\d{2}", month) is None:
        raise Exception("Month has the wrong format!")

    query(
        """
        INSERT INTO viewer_of_the_month_challenges (month, description, script_path)
        VALUES (?, ?, ?)
        """,
        (month, description, script_path)
    )


def get_user_by_username(username: str):
    users = query(
        "SELECT id, username, display_name FROM users WHERE username = ?",
        (username,))
    if len(users) == 0:
        return None

    return users[0]


def get_user_id(username: str, display_name: str):
    user_ids = query("SELECT id FROM users WHERE username = ?", (username,))

    if len(user_ids) > 0:
        return user_ids[0][0]

    query("INSERT INTO users (username, display_name) VALUES(?, ?)",
          (username, display_name))
    user_ids = query("SELECT id FROM users WHERE username = ?", (username,))
    return user_ids[0][0]


def insert_user(username: str, display_name: str):
    query("INSERT INTO users (username, display_name) VALUES(?, ?)",
          (username, display_name))


def insert_command_in_db(command: BaseCommand, user: twitchAPI.chat.ChatUser):
    command_params = command.get_params() or {}
    user_id = get_user_id(user.name, user.display_name)

    query(
        "INSERT INTO executed_commands (command, parameters, user_id, user) VALUES (?, ?, ?, ?)",
        (command.name, json.dumps(command_params), user_id, user.name)
    )


def insert_votm_winner(month, user_id, profile_img):
    frame_rotation = random.randint(-3, 3)
    challenge_id = query(
        "SELECT id FROM viewer_of_the_month_challenges WHERE month = ?",
        (month,)
    )[0][0]

    query(
        "INSERT INTO main.viewer_of_the_month_winners (challenge_id, user_id, frame_rotation, profile_image_url) VALUES(?, ?, ?, ?)",
        (challenge_id, user_id, frame_rotation, profile_img)
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='action', help='Action to execute')

    up_parser = subparsers.add_parser('up',
                                      help="Migrate DB to most current version.")
    down_parser = subparsers.add_parser('down',
                                        help="Downgrade DB. You may specify a specific version.")
    down_parser.add_argument('-v', '--to-version', type=int, nargs="?", const=0,
                             choices=[0, *get_all_migration_versions()])

    make_parser = subparsers.add_parser('make',
                                        help="Create a new migration.")

    args = parser.parse_args()

    if args.action == 'up':
        con = connect_db(config.database_path)
        migrate_db(con)

    if args.action == 'down':
        con = connect_db(config.database_path)
        downgrade_db(con, args.to_version)

    if args.action == 'make':
        create_migration(args.make)
