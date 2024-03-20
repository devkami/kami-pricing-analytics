import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from kami_pricing_analytics.interface.api.fastapi.app import app


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
        response = self.client.post('/research', json=payload)
        self.assertEqual(response.status_code, 200)

    def test_research_failure_invalid_strategy(self):
        payload = {
            'product_url': 'http://belezanaweb.com.br/product',
            'research_strategy': 99,
        }
        response = self.client.post('/research', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('detail', response.json())
        expected_detail = 'Invalid strategy option 99. Available options are: [<StrategyOptions.WEB_SCRAPING: 0>, <StrategyOptions.GOOGLE_SHOPPING: 1>]'
        self.assertEqual(response.json()['detail'], expected_detail)


if __name__ == '__main__':
    unittest.main()
