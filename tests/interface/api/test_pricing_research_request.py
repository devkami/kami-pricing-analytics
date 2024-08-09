import asyncio
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

from kami_pricing_analytics.data_collector import CollectorOptions
from kami_pricing_analytics.interface.api import (
    PricingResearchRequest,
    PricingResearchRequestException,
)
from kami_pricing_analytics.schemas import PricingResearch
from kami_pricing_analytics.services import PricingService


class TestPricingResearchRequest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.valid_data = {
            'url': 'https://www.amazon.com.br/dp/B07GYX8QRJ',
            'marketplace': 'AMAZON',
            'marketplace_id': 'B07GYX8QRJ',
            'collector_option': CollectorOptions.WEB_SCRAPING.value,
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
            self.request.collector_option, self.valid_data['collector_option']
        )
        self.assertEqual(
            self.request.store_result, self.valid_data['store_result']
        )
        self.assertIsInstance(self.request.service, PricingService)
        self.assertIsInstance(self.request.service.research, PricingResearch)

    def test_wrong_strategy_option_raises_error(self):
        self.request.collector_option = 99
        with self.assertRaises(PricingResearchRequestException):
            self.request.validate_strategy_option()

    def test_missing_url_and_marketplace_info_raises_error(self):
        self.request.url = None
        self.request.marketplace = None
        with self.assertRaises(PricingResearchRequestException):
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
        async def mock_create_task_func(coro):
            await coro

        mock_create_task.side_effect = mock_create_task_func
        self.request.store_result = True

        await self.request.post()

        mock_create_task.assert_called_once()
        called_coro = mock_create_task.call_args[0][0]

        self.assertTrue(
            asyncio.iscoroutine(called_coro),
            'Expected a coroutine to be scheduled for create_task.',
        )
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

    @patch(
        'kami_pricing_analytics.services.pricing_service.PricingService.retrieve_research'
    )
    async def test_get_success_not_expired(self, mock_retrieve_research):
        self.request.service.research.sellers = ['seller1', 'seller2']
        self.request.service.research.conducted_at = datetime.now(
            tz=timezone.utc
        )

        self.assertFalse(self.request.service.research.expired)
        self.assertEqual(
            self.request.service.research.sellers, ['seller1', 'seller2']
        )

    @patch(
        'kami_pricing_analytics.services.pricing_service.PricingService.retrieve_research'
    )
    @patch(
        'kami_pricing_analytics.interface.api.pricing_research_request.PricingResearchRequest.post'
    )
    async def test_get_expired_data_calls_post(
        self, mock_post, mock_retrieve_research
    ):
        self.request.service.research.sellers = ['seller1', 'seller2']
        self.request.service.research.conducted_at = datetime.now(
            tz=timezone.utc
        ) - timedelta(seconds=3600)

        await self.request.get()

        mock_post.assert_awaited()

        self.assertTrue(self.request.service.research.expired)
        self.assertEqual(
            self.request.service.research.sellers, ['seller1', 'seller2']
        )


if __name__ == '__main__':
    unittest.main()
