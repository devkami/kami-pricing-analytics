import unittest

from kami_pricing_analytics.data_collector import (
    CollectorFactory,
    CollectorOptions,
)
from kami_pricing_analytics.data_collector.strategies.web_scraping import (
    AmazonScraper,
    BelezaNaWebScraper,
    MercadoLibreScraper,
)


class TestCollectorFactory(unittest.TestCase):
    def test_get_amazon_scraper(self):
        scraper = CollectorFactory.get_strategy(
            CollectorOptions.WEB_SCRAPING.value,
            'https://www.amazon.com.br/prodcut',
        )
        self.assertIsInstance(scraper, AmazonScraper)

    def test_get_beleza_na_web_scraper(self):
        scraper = CollectorFactory.get_strategy(
            CollectorOptions.WEB_SCRAPING.value,
            'https://www.belezanaweb.com.br/prodcut',
        )
        self.assertIsInstance(scraper, BelezaNaWebScraper)

    def test_get_mercado_livre_scraper(self):
        scraper = CollectorFactory.get_strategy(
            CollectorOptions.WEB_SCRAPING.value,
            'https://www.mercadolivre.com.br/prodcut',
        )
        self.assertIsInstance(scraper, MercadoLibreScraper)

    def test_get_unsupported_url(self):
        with self.assertRaises(ValueError):
            CollectorFactory.get_strategy(
                CollectorOptions.WEB_SCRAPING.value,
                'https://www.unsupported.com.br/prodcut',
            )

    def test_get_unsupported_strategy(self):
        with self.assertRaises(ValueError):
            CollectorFactory.get_strategy(
                999,
                'https://www.amazon.com.br/prodcut',
            )


if __name__ == '__main__':
    unittest.main()
