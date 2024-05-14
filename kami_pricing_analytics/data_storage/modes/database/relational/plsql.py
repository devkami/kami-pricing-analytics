from pydantic import Field

from .storage import DatabaseSettings, DatabaseStorage


class PLSQLSettings(DatabaseSettings):
    """
    Configuration settings specific to Oracle PL/SQL database.

    Attributes:
        db_driver (str): Database driver, defaulting to 'oracle+cx_oracle'.
        db_port (int): Database port, default is 1521.
    """

    db_driver: str = 'oracle+cx_oracle'
    db_port: int = Field(default=1521)

    @property
    def db_url(self):
        return f'{self.db_driver}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'


class PLSQLStorage(DatabaseStorage):
    """Storage class for Oracle PL/SQL database using the specified settings."""

    def __init__(self, settings: PLSQLSettings):
        super().__init__(settings)
