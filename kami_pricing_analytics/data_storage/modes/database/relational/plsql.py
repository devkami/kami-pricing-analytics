from pydantic import Field

from kami_pricing_analytics.data_storage.modes.database.relational.storage import (
    DatabaseSettings,
    DatabaseStorage,
)


class PLSQLSettings(DatabaseSettings):
    db_driver: str = 'oracle+cx_oracle'
    db_port: int = Field(default=1521)

    @property
    def db_url(self):
        return f'{self.db_driver}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'


class PLSQLStorage(DatabaseStorage):
    def __init__(self, settings: PLSQLSettings):
        super().__init__(settings)
