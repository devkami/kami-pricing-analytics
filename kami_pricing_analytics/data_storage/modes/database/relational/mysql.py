from pydantic import Field

from .storage import DatabaseSettings, DatabaseStorage


class MySQLSettings(DatabaseSettings):
    """
    Configuration settings specific to MySQL database.

    Attributes:
        db_driver (str): Database driver, defaulting to 'mysql+aiomysql'.
        db_port (int): Database port, default is 3306.
    """

    db_driver: str = 'mysql+aiomysql'
    db_port: int = Field(default=3306)

    @property
    def db_url(self) -> str:
        """Constructs the database URL based on the MySQL settings."""
        return f'{self.db_driver}://{self.db_user}:{self.db_password.get_secret_value()}@{self.db_host}:{self.db_port}/{self.db_name}'


class MySQLStorage(DatabaseStorage):
    """Storage class for MySQL database using the specified settings."""

    def __init__(self, settings: MySQLSettings):
        super().__init__(settings)
