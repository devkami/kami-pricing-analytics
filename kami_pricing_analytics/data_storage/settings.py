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

class PostgreSQLSettings(DatabaseSettings):    
    db_driver: str = 'postgresql+asyncpg'
    db_port: int = Field(default=5432)
    @property
    def db_url(self):
        return f'{self.db_driver}://{self.db_user}:{self.db_password.get_secret_value()}@{self.db_host}:{self.db_port}/{self.db_name}'


class MySQLSettings(DatabaseSettings):
    db_driver: str = 'mysql+aiomysql'
    db_port: int = Field(default=3306)


class SQLServerSettings(DatabaseSettings):
    db_driver: str = 'mssql+aiomssql'
    db_port: int = Field(default=1433)
    

class PLSQLSettings(DatabaseSettings):
    db_driver: str = 'oracle+cx_oracle'
    db_port: int = Field(default=1521)


class SQLiteSettings(DatabaseSettings):    
    db_driver: str = 'sqlite+aiosqlite'
    db_port: int = Field(default=0)
    @property
    def db_url(self):
        db_url = self.db_name if self.db_name == ':memory:' else f'{self.db_name}.db'
        return f'{self.db_driver}:///{db_url}'
