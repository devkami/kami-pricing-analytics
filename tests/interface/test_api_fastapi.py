import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from kami_pricing_analytics.data_collector.strategies.web_scraping.beleza_na_web import (
    BelezaNaWebScraper,
)
from kami_pricing_analytics.interface.api.fastapi.app import app
from kami_pricing_analytics.schemas.options import StrategyOptions

available_strategies = [
    f'{strategy.value}: {strategy.name}' for strategy in StrategyOptions
]


class TestFastAPIResearchEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch(
        'kami_pricing_analytics.schemas.pricing_research.PricingResearch.conduct_research',
        new_callable=AsyncMock,
    )
    def test_research_success(self, mock_conduct_research):
        mock_conduct_research.return_value = {'result': 'mocked data'}

        payload = {
            'product_url': 'http://belezanaweb.com.br/product',
            'research_strategy': 0,
        }
        response = self.client.post('/api/research', json=payload)
        self.assertEqual(response.status_code, 200)

    def test_research_failure_invalid_strategy(self):
        payload = {
            'product_url': 'http://belezanaweb.com.br/product',
            'research_strategy': 99,
        }
        response = self.client.post('/research', json=payload)
        self.assertEqual(response.status_code, 404)
        self.assertIn('detail', response.json())

    @patch(
        'kami_pricing_analytics.data_collector.strategies.web_scraping.base_scraper.BaseScraper.get_http_client'
    )
    async def test_user_agent_prevents_timeout(self, mock_get_http_client):
        # Mocking http client and it's behavior
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<html></html>'

        # Simulate async context manager behavior with the mock
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get.return_value = mock_response

        mock_get_http_client.return_value = mock_client

        # Create instance of the scraper
        scraper = BelezaNaWebScraper(
            product_url='http://belezanaweb.com.br/product',
            logger_name='test_logger',
        )

        # Execute the fetch_content method which should internally use the mocked http client
        content = await scraper.fetch_content()

        # Verify that the get method of the mock client was called with the correct User-Agent header
        mock_client.get.assert_called_with(
            'https://www.belezanaweb.com.br/robots.txt',
            headers={
                'User-Agent': 'YourUserAgentHere'
            },  # Ensure this matches the actual user agent used in your class
        )

        # Assertions to verify behavior - adjust as necessary based on your actual test requirements
        self.assertEqual(content, '<html></html>')


if __name__ == '__main__':
    unittest.main()
