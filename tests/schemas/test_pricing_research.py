import unittest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from pydantic import ValidationError

from kami_pricing_analytics.data_collector.strategies.web_scraping.beleza_na_web import (
    BelezaNaWebScraper,
)
from kami_pricing_analytics.schemas.pricing_research import PricingResearch


class TestPricingResearch(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.valid_data = {
            'id': 1,
            'sku': 'SKU12345',
            'description': 'A test product',
            'url': 'http://belezanaweb.com/product',
            'conducted_at': datetime.now(tz=timezone.utc),
            'result': {'key': 'value'},
        }
        self.invalid_data_types = {
            'id': 'not an integer',
            'sku': 12345,
            'description': True,
            'url': 'not a valid URL',
            'conducted_at': 'not a datetime',
            'result': 'not a dict',
        }

    def test_success_create_instance_with_minimum_required_fields(self):
        instance = PricingResearch(url=self.valid_data['url'])
        self.assertEqual(str(instance.url), self.valid_data['url'])

    def test_failure_with_invalid_data_for_each_field(self):
        for field, value in self.invalid_data_types.items():
            with self.assertRaises(ValidationError):
                PricingResearch(**{field: value})

    def test_success_define_web_scraping_strategy(self):
        instance = PricingResearch(url=self.valid_data['url'])
        instance.set_strategy(0)
        print(f'instance: {instance}')
        self.assertIsInstance(instance.strategy, BelezaNaWebScraper)

    def test_failure_define_web_scraping_strategy(self):
        instance = PricingResearch(url=self.valid_data['url'])
        with self.assertRaises(ValueError):
            instance.set_strategy(99)

    @patch(
        'kami_pricing_analytics.data_collector.strategies.web_scraping.beleza_na_web.BelezaNaWebScraper.execute',
        new_callable=AsyncMock,
    )
    async def test_success_conduct_research(self, mock_execute):

        mock_execute.return_value = {
            'key': 'value'
        }  # Correctly set the return value

        instance = PricingResearch(**self.valid_data)
        instance.set_strategy(
            0
        )  # Assuming 0 correctly sets to web_scraping strategy
        await instance.conduct_research()  # Use await here since conduct_research is async

        self.assertEqual(instance.result, {'key': 'value'})


if __name__ == '__main__':
    unittest.main()
