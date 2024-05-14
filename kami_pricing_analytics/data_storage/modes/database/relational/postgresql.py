from pydantic import Field

from .storage import DatabaseSettings, DatabaseStorage


class PostgreSQLSettings(DatabaseSettings):
    """
    Configuration settings specific to PostgreSQL database.

    Attributes:
        db_driver (str): Database driver, defaulting to 'postgresql+asyncpg'.
        db_port (int): Database port, default is 5432.
    """

    db_driver: str = 'postgresql+asyncpg'
    db_port: int = Field(5432)

    @property
    def db_url(self) -> str:
        """Constructs the database URL based on the PostgreSQL settings."""
        return f'{self.db_driver}://{self.db_user}:{self.db_password.get_secret_value()}@{self.db_host}:{self.db_port}/{self.db_name}'


class PostgreSQLStorage(DatabaseStorage):
    """Storage class for PostgreSQL database using the specified settings."""

    def __init__(self, settings: PostgreSQLSettings):
        super().__init__(settings)
