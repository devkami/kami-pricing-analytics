import logging
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from urllib.parse import urlparse

import httpx
from pydantic import ConfigDict, Field
from robotexclusionrulesparser import RobotExclusionRulesParser as Robots

from kami_pricing_analytics.data_collector.strategies.base_strategy import (
    BaseStrategy,
)
from kami_pricing_analytics.data_collector.strategies.web_scraping.constants import (
    DEFAULT_CRAWL_DELAY,
    DEFAULT_USER_AGENT,
)


class BaseScraper(BaseStrategy):
    user_agent: str = Field(default=DEFAULT_USER_AGENT)
    http_client: httpx.AsyncClient = Field(default=None)
    base_url: str = Field(default='')
    robots_url: str = Field(default='')
    crawl_delay: int = Field(default=DEFAULT_CRAWL_DELAY)
    logger_name: str = Field(default='pricing-scraper')
    logger: logging.Logger = Field(default=None)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data):
        super().__init__(**data)
        self.base_url = self.product_url.scheme + '://' + self.product_url.host
        self.robots_url = f'{self.base_url}/robots.txt'
        self._crawl_delay_fetched = False
        self.set_logger(self.logger_name)

    @asynccontextmanager
    async def get_http_client(self):
        headers = {'User-Agent': self.user_agent}
        async with httpx.AsyncClient(headers=headers) as client:
            yield client

    async def _get_crawl_delay_async(self) -> int:
        rules = Robots()
        try:
            async with self.get_http_client() as client:
                response = await client.get(self.robots_url)
            rules.parse(response.text)
            user_agent = DEFAULT_USER_AGENT
            delay = rules.get_crawl_delay(user_agent)
            return delay if delay is not None else DEFAULT_CRAWL_DELAY
        except Exception as e:
            self.logger.exception(f'Error getting crawl delay: {e}')
            return DEFAULT_CRAWL_DELAY

    async def _ensure_crawl_delay(self):
        if not self._crawl_delay_fetched:
            self.crawl_delay = await self._get_crawl_delay_async()
            self._crawl_delay_fetched = True

    def _get_base_url(self) -> str:
        parsed_url = urlparse(str(self.product_url))
        return f'{parsed_url.scheme}://{parsed_url.netloc}'

    def set_logger(self, logger_name: str):
        self.logger = logging.getLogger(logger_name)

    async def fetch_content(self) -> str:
        await self._ensure_crawl_delay()
        async with self.get_http_client() as client:
            response = await client.get(str(self.product_url))
        return response.text

    @abstractmethod
    async def scrap_product(self) -> list:
        pass

    async def close_http_client(self):
        await self.http_client.aclose()
