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
from kami_pricing_analytics.services import (
    PricingService,
    PricingServiceException,
)


class TestPricingResearchRequest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.valid_data = {
            'url': 'https://www.belezanaweb.com.br/product',
            'marketplace': 'beleza_na_web',
            'marketplace_id': '12345',
            'collector_option': CollectorOptions.WEB_SCRAPING.value,
            'store_result': True,
        }
        self.request = PricingResearchRequest(**self.valid_data)

    def test_create_instance_with_valid_post_data(self):
        self.assertEqual(self.request.url, self.valid_data['url'])
        self.assertEqual(
            self.request.marketplace, self.valid_data['marketplace']
        )
        self.assertEqual(
            self.request.marketplace_id, self.valid_data['marketplace_id']
        )
        self.assertEqual(
            self.request.collector_option,
            self.valid_data['collector_option'],
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
        'kami_pricing_analytics.services.pricing_service.PricingService.retrieve_research',
        new_callable=AsyncMock,
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
        'kami_pricing_analytics.services.pricing_service.PricingService.retrieve_research',
        new_callable=AsyncMock,
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

    @patch(
        'kami_pricing_analytics.data_storage.modes.database.relational.sqlite.SQLiteStorage',
        new_callable=AsyncMock,
    )
    @patch(
        'kami_pricing_analytics.interface.api.pricing_research_request.PricingResearchRequest.post',
        new_callable=AsyncMock,
    )
    async def test_get_for_beleza_na_web_without_url_raises_error(
        self, mock_post, mock_storage_retrieve
    ):
        mock_storage_retrieve.return_value = []
        mock_post.return_value = None

        self.request = PricingResearchRequest(
            marketplace='beleza_na_web', marketplace_id='12345'
        )
        self.request.service = PricingService(
            collector_option=self.request.collector_option,
            research=self.request.service.research,
            store_result=self.request.store_result,
            storage_mode=self.request.service.storage_mode,
        )
        self.request.service.storage = mock_storage_retrieve
        self.request.service.storage.retrieve.return_value = []

        with self.assertRaises(PricingServiceException) as context:
            await self.request.get()

        self.assertIn('Product URL is required', str(context.exception))
        mock_post.assert_not_awaited()

    @patch(
        'kami_pricing_analytics.data_storage.modes.database.relational.sqlite.SQLiteStorage.retrieve',
        new_callable=AsyncMock,
    )
    @patch(
        'kami_pricing_analytics.services.pricing_service.PricingService.retrieve_research',
        new_callable=AsyncMock,
    )
    async def test_get_for_beleza_na_web_expired_uses_stored_url(
        self, mock_retrieve_research, mock_storage_retrieve
    ):
        mock_storage_retrieve.return_value = [
            {
                'url': 'https://www.belezanaweb.com.br/product',
                'marketplace': 'beleza_na_web',
                'marketplace_id': '12345',
                'brand': 'Test Brand',
                'description': 'Test Description',
                'category': 'Cosmetics',
                'conducted_at': datetime.now(tz=timezone.utc)
                - timedelta(days=1),
            }
        ]
        mock_retrieve_research.return_value = True

        self.request.service.research.conducted_at = datetime.now(
            tz=timezone.utc
        ) - timedelta(days=1)
        self.request.service.research.url = (
            'https://www.belezanaweb.com.br/product'
        )

        await self.request.get()

        self.assertEqual(
            self.request.service.research.url,
            'https://www.belezanaweb.com.br/product',
        )
        mock_retrieve_research.assert_awaited_once()


if __name__ == '__main__':
    unittest.main()
