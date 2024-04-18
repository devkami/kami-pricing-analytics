import unittest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from pydantic import ValidationError

from kami_pricing_analytics.data_collector.strategies.web_scraping.amazon import (
    AmazonScraper,
)
from kami_pricing_analytics.schemas.pricing_research import PricingResearch


class TestPricingResearch(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.valid_data = {
            'id': 1,
            'sku': 'SKU12345',
            'marketplace': 'amazon',
            'marketplace_id': 'MLB-3340422055',
            'description': 'A test product',
            'url': 'https://www.amazon.com.br/dp/MLB-3340422055',
            'conducted_at': datetime.now(tz=timezone.utc),
            'result': {'key': 'value'},
        }
        self.invalid_data_types = {
            'id': 'not an integer',
            'marketplace': 'not a valid marketplace',
            'sku': 12345,
            'description': True,
            'url': 'not a valid URL',
            'conducted_at': 'not a datetime',
            'result': 'not a dict',
        }

    def test_create_instance_with_only_url(self):
        instance = PricingResearch(url=self.valid_data['url'])
        self.assertEqual(str(instance.url), self.valid_data['url'])

    def test_create_instance_with_marketplace_info(self):
        instance = PricingResearch(
            url=self.valid_data['url'],
            marketplace=self.valid_data['marketplace'],
            marketplace_id=self.valid_data['marketplace_id'],
        )
        self.assertEqual(instance.marketplace, self.valid_data['marketplace'])
        self.assertEqual(
            instance.marketplace_id, self.valid_data['marketplace_id']
        )

    def test_failure_with_missing_required_fields(self):
        with self.assertRaises(ValueError):
            PricingResearch(maekretplace=self.valid_data['marketplace'])

    def test_set_url_with_correct_marketplace_info(self):
        instance = PricingResearch(
            marketplace=self.valid_data['marketplace'],
            marketplace_id=self.valid_data['marketplace_id'],
        )
        instance.set_url()
        self.assertEqual(
            instance.url,
            'https://www.amazon.com.br/dp/MLB-3340422055',
        )

    def test_set_url_with_incorrect_marketplace_info(self):
        with self.assertRaises(ValueError):
            instance = PricingResearch(
                marketplace='not a valid marketplace',
                marketplace_id='MLB-3340422055',
            )

    def test_failure_with_invalid_data_for_each_field(self):
        for field, value in self.invalid_data_types.items():
            with self.assertRaises(ValidationError):
                PricingResearch(**{field: value})

    def test_extract_marketplace_from_url(self):
        instance = PricingResearch(url=self.valid_data['url'])
        self.assertEqual(instance.marketplace, 'amazon')

    def test_extract_marketplace_id_from_url(self):
        instance = PricingResearch(url=self.valid_data['url'])
        self.assertEqual(instance.marketplace_id, 'MLB-3340422055')

    def test_get_marketplace_info_from_url(self):
        instance = PricingResearch(url=self.valid_data['url'])
        self.assertEqual(instance.marketplace, 'amazon')
        self.assertEqual(instance.marketplace_id, 'MLB-3340422055')

    def test_success_define_web_scraping_strategy(self):
        instance = PricingResearch(url=self.valid_data['url'])
        instance.set_strategy(0)
        self.assertIsInstance(instance.strategy, AmazonScraper)

    def test_failure_define_web_scraping_strategy(self):
        instance = PricingResearch(url=self.valid_data['url'])
        with self.assertRaises(ValueError):
            instance.set_strategy(99)

    @patch(
        'kami_pricing_analytics.data_collector.strategies.web_scraping.amazon.AmazonScraper.execute',
        new_callable=AsyncMock,
    )
    async def test_success_conduct_research(self, mock_execute):

        mock_execute.return_value = {'key': 'value'}

        instance = PricingResearch(**self.valid_data)
        instance.set_strategy(0)
        await instance.conduct_research()

        self.assertEqual(instance.result, {'key': 'value'})

    @patch(
        'kami_pricing_analytics.data_storage.storage_factory.StorageFactory.get_mode'
    )
    async def test_store_research_success(self, mock_get_mode):
        mock_storage = AsyncMock()
        mock_storage.save = AsyncMock(return_value=None)

        mock_get_mode.return_value = mock_storage

        instance = PricingResearch(**self.valid_data)
        instance.set_storage(0)
        await instance.store_research()

        mock_storage.save.assert_awaited_once()


if __name__ == '__main__':
    unittest.main()
