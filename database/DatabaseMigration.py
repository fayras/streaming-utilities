from abc import ABC, abstractmethod
from sqlite3 import Connection


class DatabaseMigration(ABC):
    @abstractmethod
    def up(self, connection: Connection) -> None:
        pass

    @abstractmethod
    def down(self, connection: Connection) -> None:
        pass
