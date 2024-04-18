import asyncio
import logging
import random
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import parse_qs, urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager

from kami_pricing_analytics.data_collector.strategies.web_scraping.base_scraper import (
    BaseScraper,
)
from kami_pricing_analytics.data_collector.strategies.web_scraping.constants import (
    USER_AGENTS,
)

amazon_scraper_logger = logging.getLogger('amazon-scraper')


class AmazonScraperException(Exception):
    pass


class AmazonScraper(BaseScraper):
    def _setup_driver(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        # User-Agent Rotation
        user_agent = random.choice(USER_AGENTS)
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

    async def get_driver(self) -> WebDriver:
        with ThreadPoolExecutor() as executor:
            loop = asyncio.get_running_loop()
            future = loop.run_in_executor(executor, self._setup_driver)
            driver = await future
            return driver

    async def scrap_product(self):
        driver = await self.get_driver()
        driver.get(str(self.product_url))
        request_interval = random.uniform(1, 3)
        amazon_scraper_logger.info(
            f'Waiting {request_interval} seconds before scraping product'
        )
        time.sleep(request_interval)

        sellers_list = []
        try:
            asin = driver.find_element(
                By.XPATH,
                '//th[contains(text(), "ASIN")]/following-sibling::td',
            ).text.strip()
            description = driver.find_element(By.ID, 'title').text.strip()
            brand = driver.find_element(
                By.XPATH,
                '//th[contains(text(), "Fabricante")]/following-sibling::td',
            ).text.strip()
            clickable_element = driver.find_element(
                By.CSS_SELECTOR, 'a.a-touch-link.a-box.olp-touch-link'
            )
            clickable_element.click()
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'aod-offer-list'))
            )
            offers = driver.find_elements(
                By.CSS_SELECTOR, '#aod-offer-list #aod-offer'
            )

            for offer in offers:
                price = offer.find_element(
                    By.CSS_SELECTOR, 'span.a-offscreen'
                ).get_attribute('innerHTML')
                seller_name = offer.find_element(
                    By.CSS_SELECTOR, 'a.a-size-small.a-link-normal'
                ).get_attribute('innerHTML')
                seller_link = offer.find_element(
                    By.CSS_SELECTOR, 'a.a-size-small.a-link-normal'
                ).get_attribute('href')
                seller_id = parse_qs(urlparse(seller_link).query).get(
                    'seller', [None]
                )[0]
                seller_info = {
                    'marketplace_id': asin,
                    'brand': brand,
                    'description': description,
                    'price': price,
                    'seller_id': seller_id,
                    'seller_name': seller_name,
                }
                sellers_list.append(seller_info)

        except Exception as e:
            raise AmazonScraperException(f'Error when scraping product: {e}')

        finally:
            driver.quit()
            return sellers_list

    async def execute(self) -> dict:
        return {'result': await self.scrap_product()}
