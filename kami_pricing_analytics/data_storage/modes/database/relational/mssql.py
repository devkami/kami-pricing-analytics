from pydantic import Field

from .storage import DatabaseSettings, DatabaseStorage


class SQLServerSettings(DatabaseSettings):
    """
    Configuration settings specific to Microsoft SQL Server.

    Attributes:
        db_driver (str): Database driver, defaulting to 'mssql+aiomssql'.
        db_port (int): Database port, default is 1433.
    """

    db_driver: str = 'mssql+aiomssql'
    db_port: int = Field(default=1433)

    @property
    def db_url(self) -> str:
        """Constructs the database URL based on the SQL Server settings."""
        return f'{self.db_driver}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'


class SQLServerStorage(DatabaseStorage):
    """Storage class for Microsoft SQL Server using the specified settings."""

    def __init__(self, settings: SQLServerSettings):
        super().__init__(settings)
