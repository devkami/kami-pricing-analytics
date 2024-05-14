import json
import unittest
from unittest.mock import MagicMock, patch

from selenium.webdriver.remote.webelement import WebElement

from kami_pricing_analytics.data_collector.strategies.web_scraping import (
    BelezaNaWebScraper,
)


class TestBelezaNaWebScraper(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.scraper = BelezaNaWebScraper(
            product_url='https://www.belezanaweb.com.br/some-product',
        )
        self.seller_data = {
            'sku': 'SKU12345',
            'brand': 'Natura',
            'name': 'Shampoo Anticaspa',
            'price': 'R$29,90',
            'seller': {
                'id': '9876',
                'name': 'Beleza na Web Store',
            },
        }
        self.scraper.webdriver = MagicMock()

    async def test_get_marketplace_id(self):
        marketplace_id = await self.scraper.get_marketplace_id(
            self.seller_data
        )
        self.assertEqual(marketplace_id, self.seller_data['sku'])

    async def test_get_brand(self):
        brand = await self.scraper.get_brand(self.seller_data)
        self.assertEqual(brand, self.seller_data['brand'])

    async def test_get_description(self):
        description = await self.scraper.get_description(self.seller_data)
        self.assertEqual(description, self.seller_data['name'])

    async def test_get_price(self):
        price = await self.scraper.get_price(self.seller_data)
        self.assertEqual(price, self.seller_data['price'])

    async def test_get_seller_id(self):
        seller_id = await self.scraper.get_seller_id(self.seller_data)
        self.assertEqual(seller_id, self.seller_data['seller']['id'])

    async def test_get_seller_name(self):
        seller_name = await self.scraper.get_seller_name(self.seller_data)
        self.assertEqual(seller_name, self.seller_data['seller']['name'])

    @patch('selenium.webdriver.Chrome.find_elements')
    async def test_get_sellers_list_success(self, mock_find_elements):
        mock_web_element = MagicMock(spec=WebElement)
        mock_seller_data = json.dumps(
            [
                {
                    'sku': 'SKU12345',
                    'brand': 'Natura',
                    'name': 'Shampoo Anticaspa',
                    'price': 'R$29,90',
                    'seller': {
                        'id': '9876',
                        'name': 'Beleza na Web Store',
                    },
                }
            ]
        )
        mock_web_element.get_attribute.return_value = mock_seller_data

        mock_find_elements.return_value = [mock_web_element]
        self.scraper.webdriver.find_elements = mock_find_elements

        sellers = await self.scraper.get_sellers_list()

        expected_sellers = json.loads(mock_seller_data)
        self.assertEqual(
            len(sellers), 1, 'Sellers list should contain exactly one element.'
        )
        self.assertEqual(
            sellers,
            expected_sellers,
            'Sellers list does not match expected sellers.',
        )

    @patch.object(
        BelezaNaWebScraper, 'get_marketplace_id', return_value='SKU12345'
    )
    @patch.object(BelezaNaWebScraper, 'get_brand', return_value='Natura')
    @patch.object(
        BelezaNaWebScraper, 'get_description', return_value='Shampoo Anticaspa'
    )
    @patch.object(BelezaNaWebScraper, 'get_price', return_value='R$29,90')
    @patch.object(BelezaNaWebScraper, 'get_seller_id', return_value='9876')
    @patch.object(
        BelezaNaWebScraper,
        'get_seller_name',
        return_value='Beleza na Web Store',
    )
    async def test_get_seller_info(
        self,
        mock_name,
        mock_id,
        mock_price,
        mock_description,
        mock_brand,
        mock_marketplace_id,
    ):
        expected_seller_info = {
            'product_url': self.scraper.product_url,
            'marketplace_id': self.seller_data['sku'],
            'brand': self.seller_data['brand'],
            'description': self.seller_data['name'],
            'price': self.seller_data['price'],
            'seller_id': self.seller_data['seller']['id'],
            'seller_name': self.seller_data['seller']['name'],
            'seller_url': '',
        }

        actual_seller_info = await self.scraper.get_seller_info(
            self.seller_data
        )

        self.assertEqual(
            actual_seller_info,
            expected_seller_info,
            'Seller info does not match expected seller info.',
        )

        mock_name.assert_called_once_with(self.seller_data)
        mock_id.assert_called_once_with(self.seller_data)
        mock_price.assert_called_once_with(self.seller_data)
        mock_description.assert_called_once_with(self.seller_data)
        mock_brand.assert_called_once_with(self.seller_data)
        mock_marketplace_id.assert_called_once_with(self.seller_data)


if __name__ == '__main__':
    unittest.main()
