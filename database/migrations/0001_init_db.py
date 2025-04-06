from sqlite3 import Connection
from database.DatabaseMigration import DatabaseMigration


class InitDB(DatabaseMigration):
    def up(self, connection: Connection) -> None:
        cursor = connection.cursor()
        print("test: INIT_DB")
        cursor.execute('''
                CREATE TABLE executed_commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command VARCHAR(255),
                    parameters TEXT,
                    user VARCHAR(255),
                    timestamp TIMESTAMP default CURRENT_TIMESTAMP
                )
                ''')

    def down(self, connection: Connection) -> None:
        cursor = connection.cursor()
        cursor.execute("DROP TABLE executed_commands")
