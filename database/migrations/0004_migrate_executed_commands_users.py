from sqlite3 import Connection
from database.DatabaseMigration import DatabaseMigration


class MigrateExecutedCommandsUsers(DatabaseMigration):
    def up(self, connection: Connection) -> None:
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO users (username) SELECT DISTINCT user FROM executed_commands
        ''')
        cursor.execute('''
            ALTER TABLE executed_commands ADD COLUMN user_id INTEGER REFERENCES users(id)
        ''')
        cursor.execute('''
            UPDATE executed_commands SET user_id = (SELECT id FROM users WHERE username = executed_commands.user)
        ''')

    def down(self, connection: Connection) -> None:
        cursor = connection.cursor()
        cursor.execute('''
            ALTER TABLE executed_commands DROP COLUMN user_id 
        ''')
        cursor.execute('''
            DELETE FROM users
        ''')
