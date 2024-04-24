from urllib.parse import parse_qs, urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from kami_pricing_analytics.data_collector.strategies.web_scraping.base_scraper import (
    BaseScraper,
)


class AmazonScraperException(Exception):
    pass


class AmazonScraper(BaseScraper):
    def __init__(self, **data):
        super().__init__(**data, logger_name='amazon-scraper')

    async def get_marketplace_id(self):
        marketplace_id = ''
        try:
            marketplace_id = self.webdriver.find_element(
                By.XPATH,
                '//th[contains(text(), "ASIN")]/following-sibling::td',
            ).text.strip()
        except Exception as e:
            raise AmazonScraperException(f'Error while getting ASIN: {e}')

        return marketplace_id

    async def get_brand(self):
        brand = ''
        try:
            brand = self.webdriver.find_element(
                By.XPATH,
                '//th[contains(text(), "Fabricante")]/following-sibling::td',
            ).text.strip()
        except Exception as e:
            raise AmazonScraperException(
                f'Error while getting product brand: {e}'
            )

        return brand

    async def get_description(self):
        description = ''
        try:
            description = self.webdriver.find_element(
                By.ID, 'title'
            ).text.strip()
        except Exception as e:
            raise AmazonScraperException(
                f'Error while getting product description: {e}'
            )

        return description

    async def get_price(self, seller):
        price = ''
        try:
            price = seller.find_element(
                By.CSS_SELECTOR, 'span.a-offscreen'
            ).get_attribute('innerHTML')
        except Exception as e:
            raise AmazonScraperException(
                f'Error while getting product price: {e}'
            )

        return price

    async def get_seller_id(self, seller):
        seller_id = ''
        try:
            seller_link = seller.find_element(
                By.CSS_SELECTOR, 'a.a-size-small.a-link-normal'
            ).get_attribute('href')
            seller_id = parse_qs(urlparse(seller_link).query).get(
                'seller', [None]
            )[0]
        except Exception as e:
            raise AmazonScraperException(f'Error while getting seller id: {e}')

        return seller_id

    async def get_seller_name(self, seller):
        seller_name = ''
        try:
            seller_name = seller.find_element(
                By.CSS_SELECTOR, 'a.a-size-small.a-link-normal'
            ).get_attribute('innerHTML')
        except Exception as e:
            raise AmazonScraperException(
                f'Error while getting seller name: {e}'
            )

        return seller_name

    async def get_seller_url(self, seller):
        seller_url = ''
        try:
            seller_url = seller.find_element(
                By.CSS_SELECTOR, 'a.a-size-small.a-link-normal'
            ).get_attribute('href')
        except Exception as e:
            raise AmazonScraperException(
                f'Error while getting seller url: {e}'
            )

        return seller_url
        
    
    async def get_sellers_list(self):
        sellers = []
        try:
            self.webdriver.get(str(self.product_url))
            clickable_element = self.webdriver.find_element(
                By.XPATH,
                '//div[@class="a-section a-spacing-none daodi-content"]//a[@class="a-link-normal"]',
            )
            clickable_element.click()
            WebDriverWait(self.webdriver, 10).until(
                EC.visibility_of_element_located((By.ID, 'aod-offer-list'))
            )
            sellers_offers = self.webdriver.find_elements(
                By.CSS_SELECTOR, '#aod-offer-list #aod-offer'
            )
            for seller_offer in sellers_offers:
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
                seller['price'] = await self.get_price(seller_offer)
                seller['seller_id'] = await self.get_seller_id(seller_offer)
                seller['seller_name'] = await self.get_seller_name(
                    seller_offer
                )
                seller['seller_url'] = await self.get_seller_url(seller_offer)
                sellers.append(seller)
        except Exception as e:
            raise AmazonScraperException(
                f'Error while getting sellers list: {e}'
            )

        return sellers

    async def get_seller_info(self, seller):
        try:
            self.webdriver.get(str(self.product_url))
            seller['marketplace_id'] = await self.get_marketplace_id()
            seller['brand'] = await self.get_brand()
            seller['description'] = await self.get_description()

        except AmazonScraperException as e:
            self.logger.error(f'Error while getting seller info details: {e}')
        except Exception as e:
            self.logger.error(
                f'Unexpected error while getting seller info: {e}'
            )

        return seller
