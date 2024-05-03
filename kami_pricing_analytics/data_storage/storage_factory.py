from enum import Enum
from typing import Dict, Type

from kami_pricing_analytics.data_storage.base_storage import BaseStorage
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


class StorageModeOptions(Enum):
    SQLITE = 0
    POSTGRESQL = 1
    MYSQL = 2
    SQLSERVER = 3
    PLSQL = 4


storage_options = [
    f'{option.value} - {option.name}' for option in StorageModeOptions
]


class StorageFactory:
    storage_mapping: Dict[StorageModeOptions, Type[BaseStorage]] = {}
    settings_mapping: Dict[StorageModeOptions, Type[DatabaseSettings]] = {}

    @classmethod
    def register_mode(
        cls,
        mode: StorageModeOptions,
        storage: Type[BaseStorage],
        settings: Type[DatabaseSettings],
    ):
        cls.storage_mapping[mode] = storage
        cls.settings_mapping[mode] = settings

    @classmethod
    def get_mode(cls, mode: int) -> Type[BaseStorage]:
        storage_mode_option = StorageModeOptions(mode)
        if (
            storage_mode_option not in cls.storage_mapping
            and storage_mode_option not in cls.settings_mapping
        ):
            raise ValueError(
                f'Unsupported STORAGE_MODE: {mode}. Available options: {storage_options}'
            )
        settings_class = cls.settings_mapping.get(storage_mode_option)
        settings = settings_class()
        storage_class = cls.storage_mapping.get(storage_mode_option)
        storage_mode = storage_class(settings=settings)
        return storage_mode


class DatabaseSettingsFactory:
    settings_mapping: Dict[StorageModeOptions, Type[DatabaseSettings]] = {}

    @classmethod
    def register_settings(cls, mode: int, settings: Type[DatabaseSettings]):
        cls.settings_mapping[StorageModeOptions(mode)] = settings

    @classmethod
    def get_settings(cls, mode: int) -> Type[DatabaseSettings]:
        settings = cls.settings_mapping.get(StorageModeOptions(mode))
        if settings is None:
            raise ValueError(
                f'Unsupported Database Settings: {mode}. Available options: {storage_options}'
            )
        return settings


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

StorageFactory.register_mode(
    StorageModeOptions.SQLITE, SQLiteStorage, SQLiteSettings
)
StorageFactory.register_mode(
    StorageModeOptions.POSTGRESQL, PostgreSQLStorage, PostgreSQLSettings
)
StorageFactory.register_mode(
    StorageModeOptions.MYSQL, MySQLStorage, MySQLSettings
)
StorageFactory.register_mode(
    StorageModeOptions.SQLSERVER, SQLServerStorage, SQLServerSettings
)
StorageFactory.register_mode(
    StorageModeOptions.PLSQL, PLSQLStorage, PLSQLSettings
)
