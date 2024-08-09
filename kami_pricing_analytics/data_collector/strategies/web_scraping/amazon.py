from typing import Dict, List
from urllib.parse import parse_qs, urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .base_scraper import BaseScraper


class AmazonScraperException(Exception):
    """
    Custom exception class for AmazonScraper-related errors.
    """

    pass


class AmazonScraper(BaseScraper):
    """
    Scraper specifically designed for the Amazon marketplace. It extracts seller information such as marketplace ID, brand, description, and pricing data from product pages.

    Inherits from:
        BaseScraper (class): Abstract base class for scraping strategies.
    """

    def __init__(self, **data):
        """
        Initializes the scraper with a specific logger for 'Amazon'.
        """
        super().__init__(**data, logger_name='amazon-scraper')

    async def get_marketplace_id(self) -> str:
        """
        Extracts the marketplace ID from the product page.

        Returns:
            str: The marketplace ID.

        Raises:
            AmazonScraperException: If an error occurs during extraction.
        """
        marketplace_id = ''
        try:
            marketplace_id = self.webdriver.find_element(
                By.XPATH,
                '//th[contains(text(), "ASIN")]/following-sibling::td',
            ).text.strip()
        except Exception as e:
            raise AmazonScraperException(f'Error while getting ASIN: {e}')

        return marketplace_id

    async def get_brand(self) -> str:
        """
        Extracts the brand from the product page.

        Returns:
            str: The brand.

        Raises:
            AmazonScraperException: If an error occurs during extraction.
        """

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

    async def get_description(self) -> str:
        """
        Extracts the description from the product page.

        Returns:
            str: The description.

        Raises:
            AmazonScraperException: If an error occurs during extraction.
        """
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

    async def get_price(self, seller: WebElement) -> str:
        """
        Extracts the price from the seller's data.

        Args:
            seller (WebElement): The seller element.

        Returns:
            str: The price.

        Raises:
            AmazonScraperException: If an error occurs during extraction.
        """
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

    async def get_seller_id(self, seller: WebElement) -> str:
        """
        Extracts the seller ID from the seller's data.

        Args:
            seller (WebElement): The seller element.

        Returns:
            str: The seller ID.

        Raises:
            AmazonScraperException: If an error occurs during extraction.
        """
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

    async def get_seller_name(self, seller: WebElement) -> str:
        """
        Extracts the seller name from the seller's data.

        Args:
            seller (WebElement): The seller element.

        Returns:
            str: The seller name.

        Raises:
            AmazonScraperException: If an error occurs during extraction.
        """
        seller_name = ''
        try:
            seller_name = seller.find_element(
                By.CSS_SELECTOR, 'a.a-size-small.a-link-normal'
            ).get_attribute('innerHTML')
        except Exception as e:
            raise AmazonScraperException(
                f'Error while getting seller name: {e}'
            )

        return seller_name.strip()

    async def get_seller_url(self, seller: WebElement) -> str:
        """
        Extracts the seller URL from the seller's data.

        Args:
            seller (WebElement): The seller element.

        Returns:
            str: The seller URL.

        Raises:
            AmazonScraperException: If an error occurs during extraction.
        """
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

    async def get_sellers_list(self) -> List[Dict]:
        """
        Extracts the list of sellers from the product page.

        Returns:
            List[Dict]: A list of dictionaries, each containing data about a seller.

        Raises:
            AmazonScraperException: If an error occurs during extraction.
        """

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

    async def get_seller_info(self, seller: Dict) -> Dict:
        """
        Extracts the seller information from the product page.

        Args:
            seller (Dict): The seller element.

        Returns:
            Dict: A dictionary containing the seller's information.

        Raises:
            AmazonScraperException: If an error occurs during extraction.
        """
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
