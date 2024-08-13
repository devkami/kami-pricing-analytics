from .base_collector import CollectorOptions, MarketPlaceOptions
from .strategies.web_scraping import (
    AmazonScraper,
    BaseScraper,
    BelezaNaWebScraper,
    MercadoLibreScraper,
)


class CollectorFactory:
    """
    Factory class for creating scraper instances based on the specified strategy
    and marketplace. This class allows for the dynamic selection of scraping strategies
    based on the provided product URL, optimizing the scraping process for different
    marketplaces.

    Methods:
        get_strategy (int, str) -> BaseScraper: Returns an instance of a scraper strategy based on the marketplace identified in the product URL.
    """

    @staticmethod
    def get_strategy(
        collector_option: int, product_url: str = None, marketplace: str = None
    ) -> BaseScraper:
        """
        Determines the appropriate scraper instance to use based on the marketplace
        in the product URL and the selected strategy option.

        Args:
            collector_option (int): Numeric identifier for the scraping strategy to use.
            product_url (str): URL of the product to be scraped.
            marketplace (str): Name of the marketplace to be scraped.

        Returns:
            strategy (BaseScraper): An instance of a scraper appropriate for the identified marketplace.

        Raises:
            ValueError: If no appropriate scraper is found for the marketplace or if
                        the strategy option is not supported.
        """

        strategy = BaseScraper
        marketplace = marketplace.upper() if marketplace else None

        if collector_option != CollectorOptions.WEB_SCRAPING.value:
            raise ValueError('Unsupported strategy option')

        if not product_url and not marketplace:
            raise ValueError(
                'Product URL or marketplace are required to set up the scraper'
            )

        if (product_url and 'belezanaweb' in product_url) or (
            marketplace == MarketPlaceOptions.BELEZA_NA_WEB.name
        ):
            strategy = BelezaNaWebScraper(product_url=product_url)

        elif (product_url and 'amazon' in product_url) or (
            marketplace == MarketPlaceOptions.AMAZON.name
        ):
            strategy = AmazonScraper(product_url=product_url)

        elif (product_url and 'mercadolivre' in product_url) or (
            marketplace == MarketPlaceOptions.MERCADO_LIVRE.name
        ):
            strategy = MercadoLibreScraper(product_url=product_url)

        else:
            raise ValueError('Unsupported marketplace for web scraping')

        return strategy
