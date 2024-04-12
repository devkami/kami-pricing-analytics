from pydantic import ConfigDict, Field, SecretStr
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    db_name: str
    db_user: str
    db_password: SecretStr
    db_host: str = Field(default='localhost')
    db_port: int
    db_driver: str

    model_config = ConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
    )

    @property
    def db_url(self) -> str:
        password = (
            self.password.get_secret_value()
            if hasattr(self.password, 'get_secret_value')
            else self.password
        )
        return f'{self.driver}://{self.user}:{password}@{self.host}:{self.port}/{self.name}'
