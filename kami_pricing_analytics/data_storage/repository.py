from kami_pricing_analytics.data_storage.constants import (
    settings_classes,
    storage_classes,
)
from kami_pricing_analytics.data_storage.modes.base_mode import BaseMode


class StorageFactory:
    @staticmethod
    def get_storage_mode(storage_mode: str) -> BaseMode:
        """
        Factory method to get a storage mode instance based on the specified mode.
        """
        if storage_mode in settings_classes:
            settings_class = settings_classes[storage_mode]
            settings = settings_class()

            if storage_mode in storage_classes:
                return storage_classes[storage_mode](settings)

        else:
            raise ValueError(
                f"Unsupported storage mode '{storage_mode}'. Currently, the only supported mode is: [{settings_classes.keys()}]."
            )

        return None
