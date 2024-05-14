import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from kami_pricing_analytics.data_collector.strategies.web_scraping import (
    AmazonScraper,
)


class TestAmazonScraper(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.scraper = AmazonScraper(
            product_url='https://www.amazon.com/dp/B07GYX8QRJ',
        )
        self.seller_data = {
            'ASIN': 'B07GYX8QRJ',
            'Brand': 'Amazon',
            'Description': 'Amazon Echo Dot 3rd Generation',
            'Price': '$49.99',
            'SellerID': '12345',
            'SellerName': 'Amazon.com',
            'SellerURL': 'https://www.amazon.com/seller-profile',
        }
        self.scraper.webdriver = MagicMock()
        self.mock_seller_link_element = MagicMock(spec=WebElement)
        self.mock_seller_link_element.find_element.return_value.get_attribute.return_value = f"https://www.amazon.com/gp/aag/main?seller={self.seller_data['SellerID']}"
        self.mock_seller_name_element = MagicMock(spec=WebElement)
        self.mock_seller_name_element.find_element.return_value.get_attribute.return_value = self.seller_data[
            'SellerName'
        ]
        self.mock_price_element = MagicMock(spec=WebElement)
        self.mock_price_element.find_element.return_value.get_attribute.return_value = self.seller_data[
            'Price'
        ]

    async def test_get_marketplace_id_success(self):
        mock_element = MagicMock()
        mock_element.text = self.seller_data['ASIN']
        self.scraper.webdriver.find_element.return_value = mock_element

        marketplace_id = await self.scraper.get_marketplace_id()
        self.assertEqual(marketplace_id, self.seller_data['ASIN'])
        self.scraper.webdriver.find_element.assert_called_once_with(
            By.XPATH, '//th[contains(text(), "ASIN")]/following-sibling::td'
        )

    async def test_get_brand_success(self):
        mock_element = MagicMock()
        mock_element.text = self.seller_data['Brand']
        self.scraper.webdriver.find_element.return_value = mock_element

        brand = await self.scraper.get_brand()
        self.assertEqual(brand, self.seller_data['Brand'])
        self.scraper.webdriver.find_element.assert_called_once_with(
            By.XPATH,
            '//th[contains(text(), "Fabricante")]/following-sibling::td',
        )

    async def test_get_description_success(self):
        mock_element = MagicMock()
        mock_element.text = self.seller_data['Description']
        self.scraper.webdriver.find_element.return_value = mock_element

        description = await self.scraper.get_description()
        self.assertEqual(description, self.seller_data['Description'])
        self.scraper.webdriver.find_element.assert_called_once_with(
            By.ID, 'title'
        )

    async def test_get_seller_id(self):
        self.scraper.webdriver.find_element.return_value = (
            self.mock_seller_link_element
        )
        seller_id = await self.scraper.get_seller_id(
            self.mock_seller_link_element
        )
        self.assertEqual(seller_id, self.seller_data['SellerID'])

    async def test_get_seller_name(self):
        self.scraper.webdriver.find_element.return_value = (
            self.mock_seller_name_element
        )
        seller_name = await self.scraper.get_seller_name(
            self.mock_seller_name_element
        )
        self.assertEqual(seller_name, self.seller_data['SellerName'])

    async def test_get_price(self):
        self.scraper.webdriver.find_element.return_value = (
            self.mock_price_element
        )
        price = await self.scraper.get_price(self.mock_price_element)
        self.assertEqual(price, self.seller_data['Price'])

    async def test_get_seller_url(self):
        mock_element = MagicMock(spec=WebElement)
        expected_url = 'https://www.amazon.com/seller-profile'
        mock_element.find_element.return_value.get_attribute.return_value = (
            expected_url
        )

        self.scraper.webdriver.find_element.return_value = mock_element
        seller_url = await self.scraper.get_seller_url(mock_element)
        self.assertEqual(seller_url, expected_url)
        mock_element.find_element.assert_called_once_with(
            By.CSS_SELECTOR, 'a.a-size-small.a-link-normal'
        )

    @patch('selenium.webdriver.support.ui.WebDriverWait.until')
    @patch('selenium.webdriver.Chrome.find_elements')
    @patch(
        'kami_pricing_analytics.data_collector.strategies.web_scraping.amazon.AmazonScraper.get_price',
        new_callable=AsyncMock,
    )
    @patch(
        'kami_pricing_analytics.data_collector.strategies.web_scraping.amazon.AmazonScraper.get_seller_id',
        new_callable=AsyncMock,
    )
    @patch(
        'kami_pricing_analytics.data_collector.strategies.web_scraping.amazon.AmazonScraper.get_seller_name',
        new_callable=AsyncMock,
    )
    @patch(
        'kami_pricing_analytics.data_collector.strategies.web_scraping.amazon.AmazonScraper.get_seller_url',
        new_callable=AsyncMock,
    )
    async def test_get_sellers_list_success(
        self,
        mock_get_seller_url,
        mock_get_seller_name,
        mock_get_seller_id,
        mock_get_price,
        mock_find_elements,
        mock_wait_until,
    ):
        mock_wait_until.return_value = None
        mock_get_price.return_value = self.seller_data['Price']
        mock_get_seller_id.return_value = self.seller_data['SellerID']
        mock_get_seller_name.return_value = self.seller_data['SellerName']
        mock_get_seller_url.return_value = self.seller_data['SellerURL']

        mock_seller_offer = MagicMock(spec=WebElement)
        mock_find_elements.return_value = [mock_seller_offer]

        self.scraper.webdriver.find_element.return_value = mock_seller_offer
        self.scraper.webdriver.find_elements = mock_find_elements

        sellers = await self.scraper.get_sellers_list()

        expected_sellers = [
            {
                'product_url': self.scraper.product_url,
                'marketplace_id': '',
                'brand': '',
                'description': '',
                'price': self.seller_data['Price'],
                'seller_id': self.seller_data['SellerID'],
                'seller_name': self.seller_data['SellerName'],
                'seller_url': self.seller_data['SellerURL'],
            }
        ]
        self.assertEqual(
            len(sellers), 1, 'Sellers list should contain exactly one seller.'
        )
        self.assertEqual(
            sellers,
            expected_sellers,
            'Sellers list does not match expected sellers.',
        )

    @patch(
        'kami_pricing_analytics.data_collector.strategies.web_scraping.amazon.AmazonScraper.get_marketplace_id',
        return_value='B07GYX8QRJ',
    )
    @patch(
        'kami_pricing_analytics.data_collector.strategies.web_scraping.amazon.AmazonScraper.get_brand',
        return_value='Amazon',
    )
    @patch(
        'kami_pricing_analytics.data_collector.strategies.web_scraping.amazon.AmazonScraper.get_description',
        return_value='Amazon Echo Dot 3rd Generation',
    )
    async def test_get_seller_info(
        self, mock_get_marketplace_id, mock_get_brand, mock_get_description
    ):
        seller_info = await self.scraper.get_seller_info({})
        expected = {
            'marketplace_id': 'B07GYX8QRJ',
            'brand': 'Amazon',
            'description': 'Amazon Echo Dot 3rd Generation',
        }
        self.assertEqual(seller_info, expected)


if __name__ == '__main__':
    unittest.main()
