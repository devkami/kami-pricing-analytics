import json

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By

from kami_pricing_analytics.data_collector.strategies.web_scraping.base_scraper import (
    BaseScraper,
)


class BelezaNaWebScraperException(Exception):
    pass


class BelezaNaWebScraper(BaseScraper):
    def __init__(self, **data):
        super().__init__(**data, logger_name='beleza-na-web-scraper')

    async def get_marketplace_id(self, seller):
        try:
            marketplace_id = seller['sku']
            return marketplace_id
        except Exception as e:
            raise BelezaNaWebScraperException(
                f'Error while getting marketplace ID: {e}'
            )

    async def get_brand(self, seller):
        try:
            brand = seller['brand']
            return brand
        except Exception as e:
            raise BelezaNaWebScraperException(
                f'Error while getting brand: {e}'
            )

    async def get_description(self, seller):
        try:
            description = seller['name']
            return description
        except Exception as e:
            raise BelezaNaWebScraperException(
                f'Error while getting description: {e}'
            )

    async def get_price(self, seller):
        try:
            price = seller['price']
            return price
        except Exception as e:
            raise BelezaNaWebScraperException(
                f'Error while getting price: {e}'
            )

    async def get_seller_id(self, seller):
        try:
            seller_id = seller['seller']['id']
            return seller_id
        except Exception as e:
            raise BelezaNaWebScraperException(
                f'Error while getting seller ID: {e}'
            )

    async def get_seller_name(self, seller):
        try:
            seller_name = seller['seller']['name']
            return seller_name
        except Exception as e:
            raise BelezaNaWebScraperException(
                f'Error while getting seller name: {e}'
            )

    async def get_seller_url(self):
        return ''

    async def get_sellers_list(self):
        sellers = []
        try:
            self.webdriver.get(str(self.product_url))
            id_sellers = self.webdriver.find_elements(
                By.CSS_SELECTOR, 'a.js-add-to-cart'
            )
            for id_seller in id_sellers:
                sellers_data = id_seller.get_attribute('data-sku')
                row = json.loads(sellers_data)[0]
                sellers.append(row)
            return sellers
        except WebDriverException as wd_error:
            self.logger.error(
                f'Webdriver Error while getting sellers list: {wd_error}'
            )
            raise BelezaNaWebScraperException(
                f'Error while getting sellers list: {wd_error}'
            )

    async def get_seller_info(self, seller_info):
        seller = {
            'product_url': self.product_url,
            'marketplace_id': '',
            'brand': '',
            'description': '',
            'price': '',
            'seller_id': '',
            'seller_name': '',
            'seller_url': '',
        }

        try:
            seller['marketplace_id'] = await self.get_marketplace_id(
                seller_info
            )
            seller['brand'] = await self.get_brand(seller_info)
            seller['description'] = await self.get_description(seller_info)
            seller['price'] = await self.get_price(seller_info)
            seller['seller_id'] = await self.get_seller_id(seller_info)
            seller['seller_name'] = await self.get_seller_name(seller_info)
        except BelezaNaWebScraperException as e:
            self.logger.error(f'Error while getting seller info details: {e}')
        except Exception as e:
            self.logger.error(
                f'Unexpected error while getting seller info: {e}'
            )

        return seller
