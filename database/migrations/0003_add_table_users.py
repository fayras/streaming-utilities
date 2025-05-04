from sqlite3 import Connection
from database.DatabaseMigration import DatabaseMigration


class AddTableUsers(DatabaseMigration):
    def up(self, connection: Connection) -> None:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(255) NOT NULL,
                display_name VARCHAR(255),
                timestamp TIMESTAMP default CURRENT_TIMESTAMP
            )
            ''')

    def down(self, connection: Connection) -> None:
        cursor = connection.cursor()
        cursor.execute("DROP TABLE users")
