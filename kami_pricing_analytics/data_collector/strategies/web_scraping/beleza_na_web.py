import json
from typing import Dict, List

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By

from .base_scraper import BaseScraper


class BelezaNaWebScraperException(Exception):
    """
    Custom exception class for BelezaNaWebScraper-related errors.
    """

    pass


class BelezaNaWebScraper(BaseScraper):
    """
    Scraper specifically designed for the 'Beleza Na Web' marketplace. It extracts seller
    information such as marketplace ID, brand, description, and pricing data from product pages.

    Inherits from:
        BaseScraper (class): Abstract base class for scraping strategies.
    """

    def __init__(self, **data):
        """
        Initializes the scraper with a specific logger for 'Beleza Na Web'.
        """
        super().__init__(**data, logger_name='beleza-na-web-scraper')

    async def get_marketplace_id(self, seller) -> str:
        """
        Extracts the marketplace ID from the seller's data.

        Args:
            seller (dict): The seller information dictionary.

        Returns:
            str: The marketplace ID.

        Raises:
            BelezaNaWebScraperException: If an error occurs during extraction.
        """
        try:
            marketplace_id = seller['sku']
            return marketplace_id
        except Exception as e:
            raise BelezaNaWebScraperException(
                f'Error while getting marketplace ID: {e}'
            )

    async def get_brand(self, seller) -> str:
        """
        Extracts the brand from the seller's data.

        Args:
            seller (dict): The seller information dictionary.

        Returns:
            str: The brand.

        Raises:
            BelezaNaWebScraperException: If an error occurs during extraction.
        """
        try:
            brand = seller['brand']
            return brand
        except Exception as e:
            raise BelezaNaWebScraperException(
                f'Error while getting brand: {e}'
            )

    async def get_description(self, seller) -> str:
        """
        Extracts the description from the seller's data.

        Args:
            seller (dict): The seller information dictionary.

        Returns:
            str: The description.

        Raises:
            BelezaNaWebScraperException: If an error occurs during extraction.
        """
        try:
            description = seller['name']
            return description
        except Exception as e:
            raise BelezaNaWebScraperException(
                f'Error while getting description: {e}'
            )

    async def get_price(self, seller) -> str:
        """
        Extracts the price from the seller's data.

        Args:
            seller (dict): The seller information dictionary.

        Returns:
            str: The price.

        Raises:
            BelezaNaWebScraperException: If an error occurs during extraction.
        """
        try:
            price = seller['price']
            return price
        except Exception as e:
            raise BelezaNaWebScraperException(
                f'Error while getting price: {e}'
            )

    async def get_seller_id(self, seller) -> str:
        """
        Extracts the seller ID from the seller's data.

        Args:
            seller (dict): The seller information dictionary.

        Returns:
            str: The seller ID.

        Raises:
            BelezaNaWebScraperException: If an error occurs during extraction.
        """
        try:
            seller_id = seller['seller']['id']
            return seller_id
        except Exception as e:
            raise BelezaNaWebScraperException(
                f'Error while getting seller ID: {e}'
            )

    async def get_seller_name(self, seller) -> str:
        """
        Extracts the seller name from the seller's data.

        Args:
            seller (dict): The seller information dictionary.

        Returns:
            str: The seller name.

        Raises:
            BelezaNaWebScraperException: If an error occurs during extraction.
        """
        try:
            seller_name = seller['seller']['name']
            return seller_name
        except Exception as e:
            raise BelezaNaWebScraperException(
                f'Error while getting seller name: {e}'
            )

    async def get_seller_url(self) -> str:
        return ''

    async def get_sellers_list(self) -> List[Dict]:
        """
        Retrieves a list of sellers from the product page by scraping specific HTML elements.

        Returns:
            list: A list of dictionaries, each containing data about a seller.

        Raises:
            BelezaNaWebScraperException: If an error occurs while scraping the sellers list.
        """
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

    async def get_seller_info(self, seller_info) -> Dict:
        """
        Compiles detailed information about a seller based on provided raw data.

        Args:
            seller_info (dict): Raw seller data from which to extract details.

        Returns:
            dict: A dictionary containing detailed seller information.

        Raises:
            BelezaNaWebScraperException: If an error occurs while compiling seller details.
        """
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
            raise
        except Exception as e:
            self.logger.error(
                f'Unexpected error while getting seller info: {e}'
            )
            raise BelezaNaWebScraperException(
                f'Unexpected error while getting seller info: {e}'
            )

        return seller
