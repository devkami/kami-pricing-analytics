from typing import Dict, Type

from kami_pricing_analytics.data_storage import BaseStorage, StorageModeOptions
from kami_pricing_analytics.data_storage.modes.database.relational import (
    DatabaseSettings,
    MySQLSettings,
    MySQLStorage,
    PLSQLSettings,
    PLSQLStorage,
    PostgreSQLSettings,
    PostgreSQLStorage,
    SQLiteSettings,
    SQLiteStorage,
    SQLServerSettings,
    SQLServerStorage,
)

storage_options = [
    f'{option.value} - {option.name}' for option in StorageModeOptions
]


class StorageFactory:
    """
    Factory class for managing storage instances across different database technologies.

    Attributes:
        storage_mapping (Dict[StorageModeOptions, Type[BaseStorage]]): Maps storage modes to corresponding storage classes.
        settings_mapping (Dict[StorageModeOptions, Type[DatabaseSettings]]): Maps storage modes to corresponding settings classes.
    """

    storage_mapping: Dict[StorageModeOptions, Type[BaseStorage]] = {}
    settings_mapping: Dict[StorageModeOptions, Type[DatabaseSettings]] = {}

    @classmethod
    def register_mode(
        cls,
        mode: StorageModeOptions,
        storage: Type[BaseStorage],
        settings: Type[DatabaseSettings],
    ) -> bool:
        """
        Registers a storage mode with its corresponding storage and settings classes.

        Args:
            mode (StorageModeOptions): The storage mode identifier.
            storage (Type[BaseStorage]): The storage class.
            settings (Type[DatabaseSettings]): The settings class.

        Returns:
            bool: True if the storage mode was successfully registered, False otherwise.

        Raises:
            ValueError: If an error occurs while registering the storage mode.
        """

        is_registered = False
        try:
            cls.storage_mapping[mode] = storage
            cls.settings_mapping[mode] = settings
            is_registered = True
        except Exception as e:
            raise ValueError(f'Error while registering storage mode: {e}')

        return is_registered

    @classmethod
    def get_mode(cls, mode: int) -> Type[BaseStorage]:
        """
        Retrieves a storage instance configured with appropriate settings for the specified mode.

        Args:
            mode (int): The storage mode identifier.

        Returns:
            Type[BaseStorage]: An instance of the corresponding storage class.
        """
        storage_mode = Type[BaseStorage]
        try:
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
        except Exception as e:
            raise ValueError(f'Error while retrieving storage mode: {e}')

        return storage_mode


class DatabaseSettingsFactory:
    """
    Factory class for managing database settings instances specific to storage modes.

    Attributes:
        settings_mapping (Dict[StorageModeOptions, Type[DatabaseSettings]]): Maps storage modes to corresponding settings classes.
    """

    settings_mapping: Dict[StorageModeOptions, Type[DatabaseSettings]] = {}

    @classmethod
    def register_settings(
        cls, mode: int, settings: Type[DatabaseSettings]
    ) -> bool:
        """
        Registers database settings for a specific storage mode.

        Args:
            mode (int): The database mode identifier.
            settings (Type[DatabaseSettings]): The settings class.

        Returns:
            bool: True if the database settings were successfully registered, False otherwise.

        Raises:
            ValueError: If an error occurs while registering the database settings.
        """

        is_registered = False
        if StorageModeOptions(mode) not in StorageModeOptions:
            raise ValueError(
                f'Unsupported Database Settings: {mode}. Available options: {storage_options}'
            )

        try:
            cls.settings_mapping[StorageModeOptions(mode)] = settings
            is_registered = True
        except Exception as e:
            raise ValueError(f'Error while registering database settings: {e}')

        return is_registered

    @classmethod
    def get_settings(cls, mode: int) -> Type[DatabaseSettings]:
        """
        Retrieves the settings instance for the specified database mode.

        Args:
            mode (int): The database mode identifier.

        Returns:
            Type[DatabaseSettings]: An instance of the corresponding settings class.

        Raises:
            ValueError: If an error occurs while retrieving the database settings.
        """
        try:
            settings = cls.settings_mapping.get(StorageModeOptions(mode))
        except Exception as e:
            raise ValueError(f'Error while retrieving database settings: {e}')

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
