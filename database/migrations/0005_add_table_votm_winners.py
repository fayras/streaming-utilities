from sqlite3 import Connection
from database.DatabaseMigration import DatabaseMigration


class AddTableVOTMWinners(DatabaseMigration):
    def up(self, connection: Connection) -> None:
        cursor = connection.cursor()
        cursor.execute('''
                CREATE TABLE viewer_of_the_month_winners (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    challenge_id INTEGER,
                    user_id INTEGER,
                    frame_rotation INTEGER, -- In Degrees
                    timestamp TIMESTAMP default CURRENT_TIMESTAMP,
                    FOREIGN KEY (challenge_id) REFERENCES viewer_of_the_month_challenges(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
                ''')

    def down(self, connection: Connection) -> None:
        cursor = connection.cursor()
        cursor.execute("DROP TABLE viewer_of_the_month_winners")
