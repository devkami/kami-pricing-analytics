import unittest
from datetime import datetime, timedelta, timezone

from pydantic import ValidationError

from kami_pricing_analytics.schemas import PricingResearch


class TestPricingResearch(unittest.TestCase):
    def setUp(self):
        self.valid_data = {
            'sku': 'SKU12345',
            'url': 'https://www.amazon.com.br/dp/B07GYX8QRJ',
            'marketplace': 'AMAZON',
            'marketplace_id': 'B07GYX8QRJ',
            'description': 'A test product',
            'brand': 'Test Brand',
            'category': 'Electronics',
        }
        self.invalid_data = {
            'sku': 12345,
            'url': 'not a valid URL',
        }

    def test_create_instance_with_valid_data(self):
        instance = PricingResearch(**self.valid_data)
        self.assertEqual(str(instance.url), self.valid_data['url'])
        self.assertEqual(instance.marketplace, self.valid_data['marketplace'])

    def test_create_instance_with_invalid_data(self):
        with self.assertRaises(ValidationError):
            PricingResearch(**self.invalid_data)

    def test_url_set_from_marketplace_info(self):
        instance = PricingResearch(
            marketplace='AMAZON', marketplace_id='B07GYX8QRJ'
        )
        instance.set_url()
        self.assertEqual(instance.url, self.valid_data['url'])

    def test_marketplace_info_extracted_from_url(self):
        instance = PricingResearch(
            url='https://www.amazon.com.br/dp/B07GYX8QRJ'
        )
        instance.extract_marketplace_from_url()
        self.assertEqual(instance.marketplace, 'amazon')

    def test_marketplace_id_extracted_from_url(self):
        instance = PricingResearch(
            url='https://www.amazon.com.br/dp/B07GYX8QRJ'
        )
        instance.extract_marketplace_id_from_url()
        self.assertEqual(instance.marketplace_id, 'B07GYX8QRJ')

    def test_update_research_data(self):
        instance = PricingResearch(**self.valid_data)
        result_data = [
            {
                'marketplace_id': 'B07GYX8QRJ',
                'description': 'Updated product',
                'brand': 'Updated Brand',
                'category': 'Updated Category',
            }
        ]
        instance.update_research_data(result_data)
        self.assertEqual(instance.description, 'Updated product')
        self.assertEqual(instance.brand, 'Updated Brand')
        self.assertEqual(instance.category, 'Updated Category')
        self.assertIsNotNone(instance.conducted_at)
        self.assertTrue(isinstance(instance.conducted_at, datetime))

    def test_expired_property(self):
        expired_time = datetime.now(tz=timezone.utc) - timedelta(seconds=3600)
        instance = PricingResearch(
            **self.valid_data, conducted_at=expired_time
        )
        self.assertTrue(instance.expired)

        instance.conducted_at = datetime.now(tz=timezone.utc)
        self.assertFalse(instance.expired)


if __name__ == '__main__':
    unittest.main()
