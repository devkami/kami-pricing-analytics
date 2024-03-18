import asyncio
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from robotexclusionrulesparser import RobotExclusionRulesParser as Robots

from scraper.constants import DEFAULT_CRAWL_DELAY, DEFAULT_USER_AGENT

scraper_logger = logging.getLogger('pricing-scraper')


class ScraperException(Exception):
    pass


@dataclass
class Scraper(ABC):
    product_url: str
    base_url: str = field(init=False)
    robots_url: str = field(init=False)
    crawl_delay: int = field(default=DEFAULT_CRAWL_DELAY)

    def __post_init__(self):
        self.base_url = self._get_base_url()
        self.robots_url = f'{self.base_url}/robots.txt'
        self._crawl_delay_fetched = False

    async def _ensure_crawl_delay(self):
        if not self._crawl_delay_fetched:
            self.crawl_delay = await self._get_crawl_delay_async()
            self._crawl_delay_fetched = True

    def _get_base_url(self) -> str:
        parsed_url = urlparse(self.product_url)
        return f'{parsed_url.scheme}://{parsed_url.netloc}'

    async def _get_crawl_delay_async(self) -> int:
        rules = Robots()
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(self.robots_url)
            rules.parse(r.text)

            user_agent = DEFAULT_USER_AGENT
            delay = rules.get_crawl_delay(user_agent)
            return delay if delay is not None else DEFAULT_CRAWL_DELAY
        except Exception as e:
            scraper_logger.exception(f'Error getting crawl delay: {e}')
            return DEFAULT_CRAWL_DELAY

    @abstractmethod
    async def fetch_content(self) -> str:
        pass

    @abstractmethod
    async def scrap_product(self) -> list:
        pass


@dataclass
class BelezaNaWebScraper(Scraper):
    async def fetch_content(self) -> str:
        await self._ensure_crawl_delay()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.product_url, headers={'User-Agent': DEFAULT_USER_AGENT}
            )
        return response.text

    async def scrap_product(self) -> list:
        content = await self.fetch_content()
        soup = BeautifulSoup(content, 'html.parser')
        id_sellers = soup.find_all('a', class_='js-add-to-cart')
        sellers_list = []

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


@dataclass
class ScraperFactory:
    @staticmethod
    def get_scraper(product_url: str) -> Scraper:
        if 'belezanaweb' in product_url:
            return BelezaNaWebScraper(product_url)
        else:
            raise ScraperException('Marketplace not supported')
