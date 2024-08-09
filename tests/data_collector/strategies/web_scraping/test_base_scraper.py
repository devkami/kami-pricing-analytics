import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from selenium.webdriver.chrome.webdriver import WebDriver

from kami_pricing_analytics.data_collector.strategies.web_scraping import (
    BaseScraper,
)


class MockScraper(BaseScraper):
    async def get_marketplace_id(self):
        return 'mock_marketplace_id'

    async def get_brand(self):
        return 'mock_brand'

    async def get_description(self):
        return 'mock_description'

    async def get_price(self):
        return 'mock_price'

    async def get_seller_id(self):
        return 'mock_seller_id'

    async def get_seller_name(self):
        return 'mock_seller_name'

    async def get_seller_url(self):
        return 'mock_seller_url'

    async def get_seller_info(self, seller):
        return {'id': seller, 'info': 'mock_info'}

    async def get_sellers_list(self):
        return ['seller1', 'seller2']


class TestBaseScraper(unittest.IsolatedAsyncioTestCase):
    def test_set_logger(self):
        scraper = MockScraper(product_url='https://www.mock.com')
        scraper.set_logger('mock_logger_name')
        self.assertIsNotNone(scraper.logger)
        self.assertEqual(scraper.logger.name, 'mock_logger_name')

    def test__get_base_url(self):
        scraper = MockScraper(product_url='https://www.mock.com/product/1234')
        self.assertEqual(scraper._get_base_url(), 'https://www.mock.com')

    @patch('selenium.webdriver')
    @patch('webdriver_manager.chrome.ChromeDriverManager')
    async def test_set_webdriver(self, mock_driver_manager, mock_chrome):
        mock_chrome.return_value = MagicMock()
        scraper = MockScraper(product_url='https://www.mock.com')
        with patch.object(scraper, 'logger', new=AsyncMock()) as mock_logger:
            await scraper.set_webdriver()
            mock_logger.exception.assert_not_called()
            self.assertIsInstance(scraper.webdriver, WebDriver)

    @patch('httpx.AsyncClient.get', new_callable=AsyncMock)
    async def test_fetch_content_success(self, mock_httpx_get):
        mock_httpx_get.return_value.text = 'mock_content'
        scraper = MockScraper(product_url='https://www.mock.com')
        content = await scraper.fetch_content()

        self.assertEqual(content, 'mock_content')

    @patch('httpx.AsyncClient.get', new_callable=AsyncMock)
    async def test_fetch_content_failure(self, mock_httpx_get):
        mock_response = AsyncMock()
        mock_response.return_value.text = AsyncMock(
            return_value='mock_content'
        )
        mock_httpx_get.return_value = mock_response
        mock_httpx_get.side_effect = Exception('mock_exception')
        scraper = MockScraper(product_url='https://www.mock.com')
        async_logger = AsyncMock()
        with patch.object(scraper, 'logger', async_logger):
            with self.assertRaises(Exception):
                await scraper.fetch_content()
            async_logger.exception.assert_called_once()

    @patch('selenium.webdriver')
    @patch('webdriver_manager.chrome.ChromeDriverManager')
    async def test_scrap_product(self, mock_driver_manager, mock_chrome):
        mock_chrome.return_value = MagicMock()
        scraper = MockScraper(product_url='http://mock.com')
        with patch.object(scraper, 'logger', new=AsyncMock()) as mock_logger:
            await scraper.set_webdriver()
            result = await scraper.scrap_product()
            self.assertEqual(
                result,
                [
                    {'id': 'seller1', 'info': 'mock_info'},
                    {'id': 'seller2', 'info': 'mock_info'},
                ],
            )
            mock_logger.error.assert_not_called()


if __name__ == '__main__':
    unittest.main()
