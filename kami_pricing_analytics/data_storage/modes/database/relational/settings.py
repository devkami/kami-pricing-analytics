from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    db_name: str
    db_user: str
    db_password: SecretStr
    db_host: str = Field(default='localhost')
    db_port: int
    db_driver: str

    @property
    def db_url(self) -> str:
        return f'{self.db_driver}://{self.db_user}:{self.db_password.get_secret_value()}@{self.db_host}:{self.db_port}/{self.db_name}'
