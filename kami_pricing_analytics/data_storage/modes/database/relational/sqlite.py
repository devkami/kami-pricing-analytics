from pydantic import Field

from .storage import DatabaseSettings, DatabaseStorage


class SQLiteSettings(DatabaseSettings):
    """
    Configuration settings specific to SQLite database.

    Attributes:
        db_driver (str): Database driver, defaulting to 'sqlite+aiosqlite'.
        db_port (int): Database port, not applicable for SQLite hence set to 0.
    """

    db_driver: str = 'sqlite+aiosqlite'
    db_port: int = Field(default=0)

    @property
    def db_url(self) -> str:
        """Constructs the database URL based on the SQLite settings."""
        db_url = (
            self.db_name
            if self.db_name == ':memory:'
            else f'{self.db_name}.db'
        )
        return f'{self.db_driver}:///{db_url}'


class SQLiteStorage(DatabaseStorage):
    """Storage class for SQLite database using the specified settings."""

    def __init__(self, settings: SQLiteSettings):
        super().__init__(settings=settings)
