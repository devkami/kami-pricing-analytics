import unittest
from unittest.mock import MagicMock

from selenium.webdriver.common.by import By

from kami_pricing_analytics.data_collector.strategies.web_scraping import (
    MercadoLibreScraper,
)


class TestMercadoLibreScraper(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.scraper = MercadoLibreScraper(
            product_url='https://www.mercadolivre.com.br/some-product'
        )
        seller_id = '4567'
        marketplace_id = 'MLB12345'
        self.seller_data = {
            'marketplace_id': marketplace_id,
            'brand': 'Natura',
            'description': 'Shampoo Anticaspa',
            'price': 'R$29,90',
            'seller_id': seller_id,
            'seller_name': 'Beleza na Web Store',
            'seller_url': f'https://www.mercadolivre.com.br/seller?seller_id={seller_id}&item_id={marketplace_id}',
        }
        self.scraper.webdriver = MagicMock()
        self.scraper._clean_product_description = MagicMock(
            return_value='shampoo anticaspa'
        )
        self.scraper._build_product_search_url = MagicMock(
            return_value='https://lista.mercadolivre.com.br/shampoo-anticaspa'
        )

        self.mock_seller_urls = [
            f'https://www.mercadolivre.com.br/seller?seller_id={seller_id}&item_id={marketplace_id}',
            f'https://www.mercadolivre.com.br/seller?seller_id={seller_id}&item_id={marketplace_id}',
        ]

    async def test_get_marketplace_id(self):
        marketplace_id = await self.scraper.get_marketplace_id(
            self.seller_data['seller_url']
        )
        self.assertEqual(marketplace_id, self.seller_data['marketplace_id'])

    async def test_get_brand(self):
        mock_element = MagicMock()
        mock_element.text = self.seller_data['brand']
        self.scraper.webdriver.find_element.return_value = mock_element
        brand = await self.scraper.get_brand()

        self.assertEqual(brand, self.seller_data['brand'])
        self.scraper.webdriver.find_element.assert_called_once_with(
            By.XPATH,
            "//span[contains(text(), 'Marca:')]/following-sibling::span",
        )

    async def test_get_description(self):
        mock_element = MagicMock()
        mock_element.text = self.seller_data['description']
        self.scraper.webdriver.find_element.return_value = mock_element
        description = await self.scraper.get_description()
        self.assertEqual(description, self.seller_data['description'])
        self.scraper.webdriver.find_element.assert_called_once_with(
            By.CSS_SELECTOR, 'h1.ui-pdp-title'
        )

    async def test_get_price(self):
        mock_price_container = MagicMock()
        mock_fraction = MagicMock()
        mock_fraction.text = self.seller_data['price'][2:-3]
        mock_currency_symbol = MagicMock()
        mock_currency_symbol.text = self.seller_data['price'][:2]
        mock_cents = MagicMock()
        mock_cents.text = self.seller_data['price'][-2:]

        mock_price_container.find_element.side_effect = [
            mock_currency_symbol,
            mock_fraction,
            mock_cents,
        ]

        self.scraper.webdriver.find_element.return_value = mock_price_container

        price = await self.scraper.get_price()
        self.assertEqual(price, self.seller_data['price'])
        self.scraper.webdriver.find_element.assert_called_with(
            By.CSS_SELECTOR, 'span.andes-money-amount.ui-pdp-price__part'
        )

    async def test_get_seller_id(self):
        seller_id = await self.scraper.get_seller_id(
            self.seller_data['seller_url']
        )
        self.assertEqual(seller_id, self.seller_data['seller_id'])

    async def test_get_seller_name(self):
        mock_element = MagicMock()
        mock_element.text = self.seller_data['seller_name']
        self.scraper.webdriver.find_element.return_value = mock_element
        seller_name = await self.scraper.get_seller_name()
        self.assertEqual(seller_name, self.seller_data['seller_name'])

    async def test_get_seller_url(self):
        mock_element = MagicMock()
        mock_element.get_attribute.return_value = self.seller_data[
            'seller_url'
        ]
        self.scraper.webdriver.find_element.return_value = mock_element

        seller_url = await self.scraper.get_seller_url()
        self.assertEqual(seller_url, self.seller_data['seller_url'])


if __name__ == '__main__':
    unittest.main()
