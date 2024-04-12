from enum import Enum
from typing import Any, Dict, Type

from kami_pricing_analytics.data_storage.modes.database.relational.mssql import (
    SQLServerSettings,
    SQLServerStorage,
)
from kami_pricing_analytics.data_storage.modes.database.relational.mysql import (
    MySQLSettings,
    MySQLStorage,
)
from kami_pricing_analytics.data_storage.modes.database.relational.plsql import (
    PLSQLSettings,
    PLSQLStorage,
)
from kami_pricing_analytics.data_storage.modes.database.relational.postgresql import (
    PostgreSQLSettings,
    PostgreSQLStorage,
)
from kami_pricing_analytics.data_storage.modes.database.relational.settings import (
    DatabaseSettings,
)
from kami_pricing_analytics.data_storage.modes.database.relational.sqlite import (
    SQLiteSettings,
    SQLiteStorage,
)
from kami_pricing_analytics.data_storage.storage_base import DataStoreBase


class StorageModeOptions(Enum):
    SQLITE = 0
    POSTGRESQL = 1
    MYSQL = 2
    SQLSERVER = 3
    PLSQL = 4


class StorageFactory:
    storage_mapping: Dict[StorageModeOptions, Type[DataStoreBase]] = {}

    @classmethod
    def register_mode(
        cls, mode: StorageModeOptions, storage: Type[DataStoreBase]
    ):
        cls.storage_mapping[mode] = storage

    @classmethod
    def get_mode(cls, mode: StorageModeOptions) -> Type[DataStoreBase]:
        storage_mode = cls.storage_mapping.get(mode)
        if storage_mode is None:
            raise ValueError(
                f'Unsupported STORAGE_MODE: {mode}. Available options: {StorageModeOptions.__members__}'
            )
        return storage_mode


class DatabaseSettingsFactory:
    settings_mapping: Dict[StorageModeOptions, Type[DatabaseSettings]] = {}

    @classmethod
    def register_settings(
        cls, mode: StorageModeOptions, settings: Type[DatabaseSettings]
    ):
        cls.settings_mapping[mode] = settings

    @classmethod
    def get_settings(cls, mode: StorageModeOptions) -> Type[DatabaseSettings]:
        settings = cls.settings_mapping.get(mode)
        if settings is None:
            raise ValueError(
                f'Unsupported Database Settings: {mode}. Available options: {StorageModeOptions.__members__}'
            )
        return settings


StorageFactory.register_mode(StorageModeOptions.SQLITE, SQLiteStorage)
StorageFactory.register_mode(StorageModeOptions.POSTGRESQL, PostgreSQLStorage)
StorageFactory.register_mode(StorageModeOptions.MYSQL, MySQLStorage)
StorageFactory.register_mode(StorageModeOptions.SQLSERVER, SQLServerStorage)
StorageFactory.register_mode(StorageModeOptions.PLSQL, PLSQLStorage)

DatabaseSettingsFactory.register_settings(
    StorageModeOptions.SQLITE, SQLiteSettings
)
DatabaseSettingsFactory.register_settings(
    StorageModeOptions.POSTGRESQL, PostgreSQLSettings
)
DatabaseSettingsFactory.register_settings(
    StorageModeOptions.MYSQL, MySQLSettings
)
DatabaseSettingsFactory.register_settings(
    StorageModeOptions.SQLSERVER, SQLServerSettings
)
DatabaseSettingsFactory.register_settings(
    StorageModeOptions.PLSQL, PLSQLSettings
)
