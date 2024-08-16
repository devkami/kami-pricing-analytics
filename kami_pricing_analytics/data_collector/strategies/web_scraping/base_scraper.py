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

from kami_pricing_analytics.data_collector import BaseCollector

from .constants import DEFAULT_CRAWL_DELAY, DEFAULT_USER_AGENT, USER_AGENTS


class BaseScraper(BaseCollector, ABC):
    """
    Abstract base class for scraping strategies. Implements common functionalities
    for web scraping operations, including handling web drivers and HTTP clients
    with respect for robots.txt constraints.

    Attributes:
        user_agent (str): Default user agent for HTTP requests.
        http_client (httpx.AsyncClient): Async HTTP client for making requests.
        base_url (str): Base URL derived from the product URL.
        robots_url (str): URL to the robots.txt file.
        crawl_delay (int): Delay between requests as specified in robots.txt.
        logger_name (str): Name for the logger.
        logger (logging.Logger): Logger instance for logging.
        webdriver (WebDriver): Selenium WebDriver instance.
        user_agents (list): List of user agents for requests.
    """

    user_agent: str = Field(default=DEFAULT_USER_AGENT)
    http_client: httpx.AsyncClient = Field(default=None)
    base_url: str = Field(default=None)
    robots_url: str = Field(default=None)
    crawl_delay: int = Field(default=DEFAULT_CRAWL_DELAY)
    logger_name: str = Field(default='pricing-scraper')
    logger: logging.Logger = Field(default=None)
    webdriver: WebDriver = Field(default=None)
    user_agents: list = USER_AGENTS
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data):
        """
        Initializes the scraper with base URL settings and logger configuration.
        """
        super().__init__(**data)
        if self.product_url:
            self.base_url = self._get_base_url()
            self.robots_url = f'{self.base_url}/robots.txt'
        else:
            self.base_url = None
            self.robots_url = None

        self._crawl_delay_fetched = False
        self.set_logger(self.logger_name)

    def _get_base_url(self) -> str:
        """
        Extracts the base URL from the product URL.
        """
        if self.product_url:
            parsed_url = urlparse(str(self.product_url))
            return f'{parsed_url.scheme}://{parsed_url.netloc}'
        return ''

    def _setup_driver(self) -> WebDriver:
        """
        Configures and returns a headless Selenium WebDriver with random user-agent.
        Includes modifications to evade detection via `selenium_stealth`.
        """
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        user_agent = random.choice(self.user_agents)
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
        """
        Asynchronously sets up and assigns a WebDriver to this scraper instance.
        Handles exceptions and logs them appropriately.
        """
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
        """
        Context manager for HTTP client to ensure proper header setup and cleanup.
        """
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
        """
        Fetches content from the given URL using the configured HTTP client,
        respecting the crawl delay defined in robots.txt.

        Args:
            url (str): URL to fetch. If empty, uses the product URL.

        Returns:
            str: The content of the page.
        """
        await self._ensure_crawl_delay()
        async with self.get_http_client() as client:
            product_url = url if url else str(self.product_url)
            response = await client.get(product_url)
        return response.text

    @abstractmethod
    async def get_marketplace_id(self) -> str:
        """
        Abstract method to get the marketplace ID from the scraped content.
        """
        pass

    @abstractmethod
    async def get_brand(self) -> str:
        """
        Abstract method to get the brand from the scraped content.
        """
        pass

    @abstractmethod
    async def get_description(self) -> str:
        """
        Abstract method to get the description from the scraped content.
        """
        pass

    @abstractmethod
    async def get_price(self) -> str:
        """
        Abstract method to get the price from the scraped content.
        """
        pass

    @abstractmethod
    async def get_seller_id(self) -> str:
        """
        Abstract method to get the seller ID from the scraped content.
        """
        pass

    @abstractmethod
    async def get_seller_name(self) -> str:
        """
        Abstract method to get the seller name from the scraped content.
        """
        pass

    @abstractmethod
    async def get_seller_url(self) -> str:
        """
        Abstract method to get the seller URL from the scraped content.
        """
        pass

    @abstractmethod
    async def get_seller_info(self, seller) -> dict:
        """
        Abstract method to get the seller info from the scraped content.
        """
        pass

    @abstractmethod
    async def get_sellers_list(self) -> list:
        """
        Abstract method to get the sellers list from the scraped content.
        """
        pass

    async def scrap_product(self) -> list:
        """
        Orchestrates the scraping process. Initializes WebDriver, fetches sellers,
        extracts their info, and ensures cleanup. Logs errors during the process.

        Returns:
            list: List of dictionaries, each containing seller info.
        """
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

    async def execute(self) -> list:
        """
        Executes the scraping process and returns the results.

        Returns:
            list: A list of scraped data.
        """
        return await self.scrap_product()

    async def close_http_client(self):
        """
        Closes the HTTP client if it has been initialized.
        """
        if self.http_client:
            await self.http_client.aclose()
