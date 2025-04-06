import json
import os
import argparse
import sqlite3
import inspect

from importlib.util import spec_from_file_location, module_from_spec
from sqlite3 import Connection

from commands import BaseCommand
from database.DatabaseMigration import DatabaseMigration


def connect_db(path='database/bot.db'):
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


def insert_command_in_db(command: BaseCommand, username: str):
    with sqlite3.connect("database/bot.db") as connection:
        command_params = command.get_params() or {}
        db_cursor = connection.cursor()
        db_cursor.execute(
            "INSERT INTO executed_commands (command, parameters, user) VALUES (?, ?, ?)",
            (command.name, json.dumps(command_params), username)
        )
        connection.commit()
        db_cursor.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--up', action="store_true",
                        help="Migrate DB to most current version.")
    parser.add_argument('--down', type=int,
                        nargs="?", const=0,
                        choices=[0, *get_all_migration_versions()],
                        help="Downgrade DB. You may specify a specific version.")
    parser.add_argument('--make', type=str, help="Create a new migration.")

    args = parser.parse_args()
    con = connect_db("database/test.db")

    if args.up:
        migrate_db(con)

    if not args.down is None:
        downgrade_db(con, args.down)

    if not args.make is None:
        create_migration(args.make)
