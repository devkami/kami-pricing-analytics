from pydantic import Field

from kami_pricing_analytics.data_storage.modes.database.relational.storage import (
    DatabaseSettings,
    DatabaseStorage,
)


class MySQLSettings(DatabaseSettings):
    db_driver: str = 'mysql+aiomysql'
    db_port: int = Field(default=3306)

    @property
    def db_url(self):
        return f'{self.db_driver}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'


class MySQLStorage(DatabaseStorage):
    def __init__(self, settings: MySQLSettings):
        super().__init__(settings)
