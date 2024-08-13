import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

from kami_pricing_analytics.data_collector import CollectorOptions
from kami_pricing_analytics.data_collector.strategies.web_scraping import (
    BaseScraper,
)
from kami_pricing_analytics.data_storage import StorageModeOptions
from kami_pricing_analytics.data_storage.modes.database.relational import (
    SQLiteStorage,
)
from kami_pricing_analytics.schemas import PricingResearch
from kami_pricing_analytics.services import (
    PricingService,
    PricingServiceException,
)


class TestPricingService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.research = PricingResearch(url='https://amazon.com/product')
        self.pricing_service = PricingService(
            research=self.research,
            collector_option=CollectorOptions.WEB_SCRAPING.value,
            storage_mode=StorageModeOptions.SQLITE.value,
            store_result=True,
        )

    def test_default_strategy_should_be_web_scraping(self):
        self.pricing_service.set_strategy()
        self.assertIsInstance(self.pricing_service.strategy, BaseScraper)

    def test_default_storage_should_be_SQLite(self):
        self.assertIsInstance(self.pricing_service.storage, SQLiteStorage)

    @patch(
        'kami_pricing_analytics.data_collector.collector_factory.CollectorFactory.get_strategy'
    )
    def test_set_strategy_sets_correct_strategy(self, mock_get_strategy):
        mock_get_strategy.return_value = self.pricing_service.strategy
        self.pricing_service.set_strategy()
        mock_get_strategy.assert_called_once_with(
            collector_option=CollectorOptions.WEB_SCRAPING.value,
            product_url='https://amazon.com/product',
        )

    @patch(
        'kami_pricing_analytics.data_storage.storage_factory.StorageFactory.get_mode'
    )
    def test_set_storage_sets_correct_storage(self, mock_get_mode):
        mock_get_mode.return_value = self.pricing_service.storage
        self.pricing_service.set_storage()
        mock_get_mode.assert_called_once_with(
            mode=StorageModeOptions.SQLITE.value
        )

    @patch(
        'kami_pricing_analytics.data_storage.modes.database.relational.sqlite.SQLiteStorage.save',
        new_callable=AsyncMock,
    )
    async def test_store_research_calls_storage_save_when_store_result_true(
        self, mock_save
    ):
        self.pricing_service.store_result = True
        await self.pricing_service.store_research()
        mock_save.assert_awaited_once()

    @patch(
        'kami_pricing_analytics.data_collector.strategies.web_scraping.amazon.AmazonScraper.execute',
        new_callable=AsyncMock,
    )
    async def test_conduct_research_updates_research_correctly(
        self, mock_execute
    ):
        mock_execute.return_value = [
            {
                'marketplace_id': '12345',
                'brand': 'Test Brand',
                'description': 'Test Description',
                'category': 'Electronics',
            }
        ]

        self.pricing_service.store_result = False
        await self.pricing_service.conduct_research()
        mock_execute.assert_awaited_once()

        self.assertEqual(self.pricing_service.research.marketplace_id, '12345')
        self.assertEqual(self.pricing_service.research.brand, 'Test Brand')
        self.assertEqual(
            self.pricing_service.research.description, 'Test Description'
        )
        self.assertEqual(self.pricing_service.research.category, 'Electronics')

    @patch(
        'kami_pricing_analytics.data_storage.modes.database.relational.sqlite.SQLiteStorage.retrieve',
        new_callable=AsyncMock,
    )
    async def test_retrieve_research_retrieves_and_update_research_data(
        self, mock_retrieve
    ):
        mock_retrieve.return_value = [
            {
                'sku': '',
                'marketplace': 'AMAZON',
                'marketplace_id': '12345',
                'brand': 'Test Brand',
                'description': 'Test Description',
                'category': 'Electronics',
                'url': 'https://amazon.com/product',
            }
        ]

        await self.pricing_service.retrieve_research()

        mock_retrieve.assert_awaited_once()

        self.assertEqual(self.pricing_service.research.marketplace_id, '12345')
        self.assertEqual(self.pricing_service.research.brand, 'Test Brand')
        self.assertEqual(
            self.pricing_service.research.description, 'Test Description'
        )
        self.assertEqual(self.pricing_service.research.category, 'Electronics')

    @patch(
        'kami_pricing_analytics.data_collector.strategies.web_scraping.amazon.AmazonScraper.execute',
        new_callable=AsyncMock,
    )
    async def test_when_conduct_research_updates_research_correctly(
        self, mock_execute
    ):
        mock_execute.return_value = [
            {
                'marketplace_id': '12345',
                'brand': 'Test Brand',
                'description': 'Test Description',
                'category': 'Electronics',
            }
        ]

        self.pricing_service.store_result = False
        await self.pricing_service.conduct_research()
        mock_execute.assert_awaited_once()

        self.assertEqual(self.pricing_service.research.marketplace_id, '12345')
        self.assertEqual(self.pricing_service.research.brand, 'Test Brand')
        self.assertEqual(
            self.pricing_service.research.description, 'Test Description'
        )
        self.assertEqual(self.pricing_service.research.category, 'Electronics')

    @patch(
        'kami_pricing_analytics.data_storage.modes.database.relational.sqlite.SQLiteStorage.save',
        new_callable=AsyncMock,
    )
    async def test_when_store_result_is_true_call_storage_save(
        self, mock_save
    ):
        await self.pricing_service.store_research()

        self.pricing_service.storage.save.assert_awaited_once()

    @patch(
        'kami_pricing_analytics.data_storage.modes.database.relational.sqlite.SQLiteStorage.save',
        new_callable=AsyncMock,
    )
    async def test_store_research_does_not_call_save_when_store_result_false(
        self, mock_save
    ):
        self.pricing_service.store_result = False
        await self.pricing_service.store_research()

        mock_save.assert_not_called()

    @patch(
        'kami_pricing_analytics.data_storage.modes.database.relational.sqlite.SQLiteStorage.retrieve',
        new_callable=AsyncMock,
    )
    async def test_retrieve_research_with_url_success(self, mock_retrieve):
        mock_retrieve.return_value = [
            {
                'sku': '',
                'marketplace': 'BELEZA_NA_WEB',
                'marketplace_id': '12345',
                'brand': 'Test Brand',
                'description': 'Test Description',
                'category': 'Cosmetics',
                'url': 'https://www.belezanaweb.com.br/product',
            }
        ]
        self.pricing_service.research.url = (
            'https://www.belezanaweb.com.br/product'
        )
        await self.pricing_service.retrieve_research()

        mock_retrieve.assert_awaited_once_with(
            {'url': 'https://www.belezanaweb.com.br/product'}
        )

        self.assertEqual(
            self.pricing_service.research.marketplace, 'BELEZA_NA_WEB'
        )
        self.assertEqual(self.pricing_service.research.marketplace_id, '12345')
        self.assertEqual(self.pricing_service.research.brand, 'Test Brand')
        self.assertEqual(
            self.pricing_service.research.description, 'Test Description'
        )
        self.assertEqual(self.pricing_service.research.category, 'Cosmetics')

    @patch(
        'kami_pricing_analytics.data_storage.modes.database.relational.sqlite.SQLiteStorage.retrieve',
        new_callable=AsyncMock,
    )
    async def test_retrieve_research_without_url_for_beleza_na_web_raises_error(
        self, mock_retrieve
    ):
        mock_retrieve.return_value = []
        self.pricing_service.research.marketplace = 'beleza_na_web'
        self.pricing_service.research.marketplace_id = '12345'
        self.pricing_service.research.url = None

        with self.assertRaises(PricingServiceException) as context:
            await self.pricing_service.retrieve_research()

        self.assertIn('Product URL is required', str(context.exception))
        mock_retrieve.assert_awaited_once()

    @patch(
        'kami_pricing_analytics.data_storage.modes.database.relational.sqlite.SQLiteStorage.retrieve',
        new_callable=AsyncMock,
    )
    async def test_retrieve_research_expired_for_beleza_na_web_uses_stored_url(
        self, mock_retrieve
    ):
        mock_retrieve.return_value = [
            {
                'sku': '',
                'marketplace': 'BELEZA_NA_WEB',
                'marketplace_id': '12345',
                'brand': 'Test Brand',
                'description': 'Test Description',
                'category': 'Cosmetics',
                'url': 'https://www.belezanaweb.com.br/product',
                'conducted_at': datetime.now(tz=timezone.utc)
                - timedelta(days=1),
            }
        ]
        self.pricing_service.research.marketplace = 'beleza_na_web'
        self.pricing_service.research.marketplace_id = '12345'
        self.pricing_service.research.url = None

        await self.pricing_service.retrieve_research()

        mock_retrieve.assert_awaited_once()
        self.assertEqual(
            str(self.pricing_service.research.url),
            'https://www.belezanaweb.com.br/product',
        )


if __name__ == '__main__':
    unittest.main()
