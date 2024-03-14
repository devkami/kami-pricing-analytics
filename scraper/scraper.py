import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List

import httpx
from bs4 import BeautifulSoup

scraper_logger = logging.getLogger('scraper')


class Scraper(ABC):
    def __init__(self, product_url: str):
        self.product_url = product_url

    @abstractmethod
    async def fetch_content(self) -> str:
        """Fetch page content."""
        pass

    @abstractmethod
    async def scrap_product(self):
        """Extract product data."""
        pass


class BelezaNaWebScraper(Scraper):
    async def fetch_content(self) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.product_url, headers={'User-Agent': 'Mozilla/5.0'}
            )
        return response.text

    async def scrap_product(self) -> List[Dict]:
        sellers_list = []
        content = await self.fetch_content()
        soup = BeautifulSoup(content, 'html.parser')
        id_sellers = soup.find_all('a', class_='js-add-to-cart')

        for id_seller in id_sellers:
            sellers_data = id_seller.get('data-sku')
            row = json.loads(sellers_data)[0]
            seller_info = {
                'sku': row['sku'],
                'brand': row['brand'],
                'category': row['category'],
                'name': row['name'],
                'price': row['price'],
                'seller_name': row['seller']['name'],
            }
            sellers_list.append(seller_info)

        return sellers_list


class ScraperFactory:
    @staticmethod
    def get_scraper(product_url: str):
        if 'belezanaweb' in product_url:
            return BelezaNaWebScraper(product_url)
        else:
            raise ValueError('Marketplace not supported')
