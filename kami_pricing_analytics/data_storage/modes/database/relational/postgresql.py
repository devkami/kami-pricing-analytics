from pydantic import Field

from kami_pricing_analytics.data_storage.modes.database.relational.storage import (
    DatabaseSettings,
    DatabaseStorage,
)


class PostgreSQLSettings(DatabaseSettings):
    db_driver: str = 'postgresql+asyncpg'
    db_port: int = Field(5432)

    @property
    def db_url(self):
        return f'{self.db_driver}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'


class PostgreSQLStorage(DatabaseStorage):
    def __init__(self, settings: PostgreSQLSettings):
        super().__init__(settings)
