import unittest
from unittest.mock import AsyncMock, patch

from kami_pricing_analytics.data_collector.strategies.web_scraping.base_scraper import (
    BaseScraper,
)
from kami_pricing_analytics.data_storage.modes.database.relational.sqlite import (
    SQLiteStorage,
)
from kami_pricing_analytics.schemas.pricing_research import PricingResearch
from kami_pricing_analytics.services.pricing_service import PricingService


class TestPricingService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.research = PricingResearch(url='https://amazon.com/product')
        self.pricing_service = PricingService(
            research=self.research, store_result=True
        )

    def test_default_strategy_should_be_web_scraping(self):
        self.assertIsInstance(self.pricing_service.strategy, BaseScraper)

    def test_default_storage_should_be_SQLite(self):
        self.assertIsInstance(self.pricing_service.storage, SQLiteStorage)

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

        self.assertEqual(self.research.marketplace_id, '12345')
        self.assertEqual(self.research.brand, 'Test Brand')
        self.assertEqual(self.research.description, 'Test Description')
        self.assertEqual(self.research.category, 'Electronics')

    @patch(
        'kami_pricing_analytics.data_storage.modes.database.relational.sqlite.SQLiteStorage.save',
        new_callable=AsyncMock,
    )
    async def test_when_store_result_is_true_call_storage_save(
        self, mock_save
    ):
        await self.pricing_service.store_research()

        self.pricing_service.storage.save.assert_awaited_once()


if __name__ == '__main__':
    unittest.main()
