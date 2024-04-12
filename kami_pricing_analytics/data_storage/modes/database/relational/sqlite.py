from pydantic import Field

from kami_pricing_analytics.data_storage.modes.database.relational.storage import (
    DatabaseSettings,
    DatabaseStorage,
)


class SQLiteSettings(DatabaseSettings):
    db_driver: str = 'sqlite+aiosqlite'
    db_port: int = Field(default=0)

    @property
    def db_url(self):
        db_url = self.db_name if self.db_name == ':memory:' else f'{self.db_name}.db'
        return f'{self.db_driver}:///{db_url}'


class SQLiteStorage(DatabaseStorage):
    def __init__(self, settings: SQLiteSettings):
        super().__init__(settings)
