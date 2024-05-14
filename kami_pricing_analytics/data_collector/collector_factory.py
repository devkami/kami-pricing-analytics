from kami_pricing_analytics.data_collector.strategies.web_scraping.amazon import (
    AmazonScraper,
)
from kami_pricing_analytics.data_collector.strategies.web_scraping.base_scraper import (
    BaseScraper,
)
from kami_pricing_analytics.data_collector.strategies.web_scraping.beleza_na_web import (
    BelezaNaWebScraper,
)
from kami_pricing_analytics.data_collector.strategies.web_scraping.mercado_libre import (
    MercadoLibreScraper,
)
from kami_pricing_analytics.schemas.options import StrategyOptions


class StrategyFactory:
    @staticmethod
    def get_strategy(strategy_option: int, product_url: str) -> BaseScraper:
        if strategy_option == StrategyOptions.WEB_SCRAPING.value:
            if 'belezanaweb' in product_url:
                return BelezaNaWebScraper(product_url=product_url)
            if 'amazon' in product_url:
                return AmazonScraper(product_url=product_url)
            if 'mercadolivre' in product_url:
                return MercadoLibreScraper(product_url=product_url)
            raise ValueError('Unsupported marketplace for web scraping')

        raise ValueError(
            'Unsupported strategy option. Available options are: 0 (WEB_SCRAPING)'
        )
