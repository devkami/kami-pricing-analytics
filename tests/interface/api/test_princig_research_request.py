import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from kami_pricing_analytics.interface.api.pricing_research_request import (
    PricingResearchRequest,
)
from kami_pricing_analytics.schemas.options import StrategyOptions
from kami_pricing_analytics.schemas.pricing_research import PricingResearch
from kami_pricing_analytics.services.pricing_service import PricingService


class TestPricingResearchRequest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.valid_data = {
            'url': 'https://www.amazon.com.br/dp/B07GYX8QRJ',
            'marketplace': 'AMAZON',
            'marketplace_id': 'B07GYX8QRJ',
            'strategy_option': StrategyOptions.WEB_SCRAPING.value,
            'store_result': True,
        }
        self.request = PricingResearchRequest(**self.valid_data)

    def test_create_instance_with_valid_data(self):
        self.assertEqual(self.request.url, self.valid_data['url'])
        self.assertEqual(
            self.request.marketplace, self.valid_data['marketplace']
        )
        self.assertEqual(
            self.request.marketplace_id, self.valid_data['marketplace_id']
        )
        self.assertEqual(
            self.request.strategy_option, self.valid_data['strategy_option']
        )
        self.assertEqual(
            self.request.store_result, self.valid_data['store_result']
        )
        self.assertIsInstance(self.request.service, PricingService)
        self.assertIsInstance(self.request.service.research, PricingResearch)

    def test_wrong_strategy_option_raises_error(self):
        self.request.strategy_option = 99
        with self.assertRaises(ValueError):
            self.request.validate_strategy_option()

    def test_missing_url_and_marketplace_info_raises_error(self):
        self.request.url = None
        self.request.marketplace = None
        with self.assertRaises(ValueError):
            self.request.validate_research()

    @patch(
        'kami_pricing_analytics.services.pricing_service.PricingService.conduct_research',
        new_callable=AsyncMock,
    )
    @patch(
        'kami_pricing_analytics.services.pricing_service.PricingService.store_research',
        new_callable=AsyncMock,
    )
    async def test_when_not_store_result_post_should_not_call_store_research(
        self, mock_store_research, mock_conduct_research
    ):
        self.request.store_result = False
        await self.request.post()
        mock_store_research.assert_not_called()
        mock_conduct_research.assert_awaited()

    @patch('asyncio.create_task')
    @patch(
        'kami_pricing_analytics.services.pricing_service.PricingService.store_research',
        new_callable=AsyncMock,
    )
    @patch(
        'kami_pricing_analytics.services.pricing_service.PricingService.conduct_research',
        new_callable=AsyncMock,
    )
    async def test_when_store_result_post_should_create_store_research_task(
        self, mock_conduct_research, mock_store_research, mock_create_task
    ):
        mock_store_research.return_value = await asyncio.sleep(0)
        self.request.store_result = True

        await self.request.post()

        mock_create_task.assert_called_once()
        mock_conduct_research.assert_awaited()

    @patch(
        'kami_pricing_analytics.services.pricing_service.PricingService.conduct_research',
        new_callable=AsyncMock,
    )
    @patch(
        'kami_pricing_analytics.services.pricing_service.PricingService.store_research',
        new_callable=AsyncMock,
    )
    async def test_when_post_is_called_should_return_sellers(
        self, mock_store_research, mock_conduct_research
    ):
        mock_conduct_research.return_value = await asyncio.sleep(0)
        mock_store_research.return_value = await asyncio.sleep(0)

        result = await self.request.post()

        self.assertEqual(result, self.request.service.research.sellers)


if __name__ == '__main__':
    unittest.main()
