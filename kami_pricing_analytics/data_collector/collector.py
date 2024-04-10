from kami_pricing_analytics.data_collector.strategies.web_scraping.amazon import (
    AmazonScraper,
)
from kami_pricing_analytics.data_collector.strategies.web_scraping.base_scraper import (
    BaseScraper,
)
from kami_pricing_analytics.data_collector.strategies.web_scraping.beleza_na_web import (
    BelezaNaWebScraper,
)


class StrategyFactory:
    @staticmethod
    def get_strategy(strategy: str, product_url: str) -> BaseScraper:
        if strategy == 'web_scraping':
            if 'belezanaweb' in product_url:
                return BelezaNaWebScraper(
                    product_url=product_url, logger_name='belezanaweb-scraper'
                )
            if 'amazon' in product_url:
                return AmazonScraper(
                    product_url=product_url, logger_name='amazon-scraper'
                )

        raise ValueError('Unsupported strategy')
