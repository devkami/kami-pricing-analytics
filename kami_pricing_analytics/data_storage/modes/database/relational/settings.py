from pydantic import ConfigDict, Field, SecretStr
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """
    Configuration settings for the database.

    Attributes:
        db_name (str): The name of the database.
        db_user (str): The username to connect to the database.
        db_password (SecretStr): The password to connect to the database.
        db_host (str): The host of the database, defaulting to 'localhost'.
        db_port (int): The port of the database.
        db_driver (str): The driver to connect to the database.
    """

    db_name: str
    db_user: str
    db_password: SecretStr
    db_host: str = Field(default='localhost')
    db_port: int
    db_driver: str

    model_config = ConfigDict(
        title='Database Settings',
        str_strip_whitespace=True,
        env_file='.env',
        env_file_encoding='utf-8',
    )

    @property
    def db_url(self) -> str:
        """
        Constructs the database URL based on the database settings.

        Returns:
            str: The database URL.
        """
        return f'{self.db_driver}://{self.db_user}:{self.db_password.get_secret_value()}@{self.db_host}:{self.db_port}/{self.db_name}'
