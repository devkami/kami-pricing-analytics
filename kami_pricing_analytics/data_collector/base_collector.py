from abc import ABC, abstractmethod
from enum import Enum

from pydantic import BaseModel, HttpUrl


class CollectorOptions(Enum):
    """
    Enumeration of supported pricing strategies.

    Attributes:
        WEB_SCRAPING (int): Web scraping strategy.
        GOOGLE_SHOPPING (int): Google Shopping strategy.
    """

    WEB_SCRAPING = 0
    GOOGLE_SHOPPING = 1

    @classmethod
    def get_strategy_name(cls, value) -> str:
        """
        Returns the name of the strategy based on the provided value.

        Args:
            value (int): The value of the strategy.

        Returns:
            str: The name of the strategy.

        Raises:
            KeyError: If the provided value is not a valid strategy.
        """
        try:
            strategy_mapping = {
                cls.WEB_SCRAPING.value: 'web_scraping',
                cls.GOOGLE_SHOPPING.value: 'google_shopping',
            }
        except KeyError:
            raise KeyError(f'Invalid strategy value: {value}')

        return strategy_mapping.get(value, None)


class MarketPlaceOptions(Enum):
    """
    Enumeration of supported marketplaces.

    Attributes:
        BELEZA_NA_WEB (tuple): Beleza na Web marketplace.
        AMAZON (tuple): Amazon marketplace.
        MERCADO_LIVRE (tuple): Mercado Livre marketplace.
    """

    BELEZA_NA_WEB = ('beleza_na_web', None)
    AMAZON = ('amazon', 'https://www.amazon.com.br/dp/{marketplace_id}')
    MERCADO_LIVRE = (
        'mercado_livre',
        'https://produto.mercadolivre.com.br/{marketplace_id}',
    )

    def __init__(self, name, url_pattern):
        self._name = name
        self.url_pattern = url_pattern

    @staticmethod
    def format_mercado_libre_id(marketplace_id) -> str:
        """
        Formats the Mercado Livre marketplace ID.

        Args:
            marketplace_id (str): The marketplace ID.

        Returns:
            str: The formatted marketplace ID.

        Raises:
            ValueError: If the marketplace ID is not in the correct format.
        """
        marketplace_id = ''
        try:
            if not marketplace_id.startswith('MLB-'):
                if marketplace_id.startswith('MLB'):
                    marketplace_id = f'MLB-{marketplace_id[3:]}'
                else:
                    marketplace_id = f'MLB-{marketplace_id}'
        except ValueError:
            raise ValueError(f'Invalid Mercado Livre ID: {marketplace_id}')
        return marketplace_id

    def build_url(self, marketplace_id) -> str:
        """
        Builds the URL for the marketplace based on the provided marketplace ID.

        Args:
            marketplace_id (str): The marketplace ID.

        Returns:
            str: The URL for the marketplace.

        Raises:
            ValueError: If the marketplace ID is not in the correct format.
        """
        url = ''

        try:
            if self.name == 'MERCADO_LIVRE':
                marketplace_id = self.format_mercado_libre_id(
                    marketplace_id=marketplace_id
                )
            if self.url_pattern:
                url = self.url_pattern.format(marketplace_id=marketplace_id)
        except Exception as e:
            raise ValueError(f'Error building URL: {e}')
        return url


class BaseCollector(BaseModel, ABC):
    """
    Abstract base class defining a strategy for data collection or processing. This class
    serves as a template for specific strategies that work with products or resources
    identified by URLs or SKU.

    Attributes:
        product_url (HttpUrl): The URL of the product or resource that the strategy will work with.
        sku (str): The Stock Keeping Unit (SKU) of the product, if available.

    Methods:
        execute(): Abstract method that must be implemented by subclasses. This method is intended to carry out the specific actions of the strategy.
    """

    product_url: HttpUrl
    sku: str = None

    @abstractmethod
    def execute(self) -> dict:
        """
        Executes the strategy's core logic on the specified product or resource.

        This method should be implemented by subclasses to perform specific actions,
        such as data collection, analysis, or any other process relevant to the
        strategy being implemented.

        Returns:
            dict: The result of the strategy's execution. The structure of the return
            value should be documented by subclasses.
        """
        pass
