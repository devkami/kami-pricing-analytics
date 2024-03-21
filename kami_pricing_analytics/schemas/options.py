from enum import Enum


class StrategyOptions(Enum):
    WEB_SCRAPING = 0
    GOOGLE_SHOPPING = 1

    @classmethod
    def get_strategy_name(cls, value):
        strategy_mapping = {
            cls.WEB_SCRAPING.value: 'web_scraping',
            cls.GOOGLE_SHOPPING.value: 'google_shopping',
        }
        return strategy_mapping.get(value, None)


class StorageOptions(Enum):
    SQLITE = 0
    POSTGRESQL = 1

    @classmethod
    def get_storage_mode_name(cls, value):
        storage_mapping = {
            cls.SQLITE.value: 'sqlite',
            cls.POSTGRESQL.value: 'postgresql',
        }
        return storage_mapping.get(value, None)
