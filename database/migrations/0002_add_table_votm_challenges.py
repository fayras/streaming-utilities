from sqlite3 import Connection
from database.DatabaseMigration import DatabaseMigration


class InitDB(DatabaseMigration):
    def up(self, connection: Connection) -> None:
        cursor = connection.cursor()
        cursor.execute('''
                CREATE TABLE viewer_of_the_month_challenges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    month VARCHAR(7),
                    description VARCHAR(255),
                    script_path VARCHAR(255),
                    timestamp TIMESTAMP default CURRENT_TIMESTAMP
                )
                ''')

    def down(self, connection: Connection) -> None:
        cursor = connection.cursor()
        cursor.execute("DROP TABLE viewer_of_the_month_challenges")
