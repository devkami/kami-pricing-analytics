import asyncio
import logging
import random
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from urllib.parse import urlparse

import httpx
from pydantic import ConfigDict, Field
from robotexclusionrulesparser import RobotExclusionRulesParser as Robots
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager

from kami_pricing_analytics.data_collector.strategies.base_strategy import (
    BaseStrategy,
)
from kami_pricing_analytics.data_collector.strategies.web_scraping.constants import (
    DEFAULT_CRAWL_DELAY,
    DEFAULT_USER_AGENT,
    USER_AGENTS,
)


class BaseScraper(BaseStrategy, ABC):
    user_agent: str = Field(default=DEFAULT_USER_AGENT)
    http_client: httpx.AsyncClient = Field(default=None)
    base_url: str = Field(default='')
    robots_url: str = Field(default='')
    crawl_delay: int = Field(default=DEFAULT_CRAWL_DELAY)
    logger_name: str = Field(default='pricing-scraper')
    logger: logging.Logger = Field(default=None)
    webdriver: WebDriver = Field(default=None)
    user_agents: list = USER_AGENTS

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data):
        super().__init__(**data)
        self.base_url = self.product_url.scheme + '://' + self.product_url.host
        self.robots_url = f'{self.base_url}/robots.txt'
        self._crawl_delay_fetched = False
        self.set_logger(self.logger_name)

    def _setup_driver(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        user_agent = random.choice(self.user_agents)
        print(f'Using User-Agent: {user_agent}')
        options.add_argument(f'user-agent={user_agent}')

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        stealth(
            driver,
            languages=['en-US', 'en'],
            vendor='Google Inc.',
            platform='Win32',
            webgl_vendor='Intel Inc.',
            renderer='Intel Iris OpenGL Engine',
            fix_hairline=True,
        )
        return driver

    async def set_webdriver(self) -> WebDriver:
        try:
            with ThreadPoolExecutor() as executor:
                loop = asyncio.get_running_loop()
                future = loop.run_in_executor(executor, self._setup_driver)
                driver = await future
                self.webdriver = driver
        except Exception as e:
            self.logger.exception(f'Error getting webdriver: {e}')

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

    async def fetch_content(self, url: str = '') -> str:
        await self._ensure_crawl_delay()
        async with self.get_http_client() as client:
            product_url = url if url else str(self.product_url)
            response = await client.get(product_url)
        return response.text

    @abstractmethod
    async def get_marketplace_id(self) -> str:
        pass

    @abstractmethod
    async def get_brand(self) -> str:
        pass

    @abstractmethod
    async def get_description(self) -> str:
        pass

    @abstractmethod
    async def get_price(self) -> str:
        pass

    @abstractmethod
    async def get_seller_id(self) -> str:
        pass

    @abstractmethod
    async def get_seller_name(self) -> str:
        pass

    @abstractmethod
    async def get_seller_url(self) -> str:
        pass

    @abstractmethod
    async def get_seller_info(self, seller) -> dict:
        pass

    @abstractmethod
    async def get_sellers_list(self) -> list:
        pass

    async def scrap_product(self) -> list:
        try:
            await self.set_webdriver()
            sellers = await self.get_sellers_list()
            sellers_list = []
            for seller in sellers:
                try:
                    seller_info = await self.get_seller_info(seller)
                    sellers_list.append(seller_info)
                except Exception as e:
                    self.logger.error(f'Error while getting seller info: {e}')
            return sellers_list
        except WebDriverException as wd_error:
            self.logger.error(
                f'Webdriver Error while scraping product: {wd_error}'
            )
        except Exception as e:
            self.logger.error(f'Unexpected Error while scraping product: {e}')
        finally:
            if self.webdriver:
                self.webdriver.quit()

        return []

    async def execute(self) -> dict:
        return {'result': await self.scrap_product()}

    async def close_http_client(self):
        await self.http_client.aclose()
