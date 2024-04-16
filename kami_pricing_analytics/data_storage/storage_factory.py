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
    settings_mapping: Dict[StorageModeOptions, Type[DatabaseSettings]] = {}

    @classmethod
    def register_mode(
        cls,
        mode: StorageModeOptions,
        storage: Type[DataStoreBase],
        settings: Type[DatabaseSettings],
    ):
        cls.storage_mapping[mode] = storage
        cls.settings_mapping[mode] = settings

    @classmethod
    def get_mode(cls, mode: StorageModeOptions) -> Type[DataStoreBase]:
        if (
            mode not in cls.storage_mapping
            and mode not in cls.settings_mapping
        ):
            raise ValueError(
                f'Unsupported STORAGE_MODE: {mode}. Available options: {StorageModeOptions.__members__}'
            )
        settings_class = cls.settings_mapping.get(mode)
        settings = settings_class()
        storage_class = cls.storage_mapping.get(mode)
        storage_mode = storage_class(settings=settings)
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
