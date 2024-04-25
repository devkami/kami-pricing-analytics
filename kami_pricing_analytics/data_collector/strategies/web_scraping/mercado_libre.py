from urllib.parse import parse_qs, urlparse

from pydantic import Field
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from kami_pricing_analytics.data_collector.strategies.web_scraping.base_scraper import (
    BaseScraper,
)
from kami_pricing_analytics.data_collector.strategies.web_scraping.constants import (
    USER_AGENTS,
)


class MercadoLibreScraperException(Exception):
    pass


mlb_user_agents = [
    ua for ua in USER_AGENTS if not ua.startswith('Mozilla/5.0 (X11; Ubuntu;')
]


class MercadoLibreScraper(BaseScraper):
    search_url: str = Field(default='https://lista.mercadolivre.com.br')

    def __init__(self, **data):
        super().__init__(
            **data,
            logger_name='mercado-libre-scraper',
            user_agents=mlb_user_agents,
        )

    def _clean_product_description(self, product_description: str) -> str:
        product_description = product_description.lower()
        product_description = ''.join(
            e for e in product_description if e.isalnum() or e.isspace()
        )
        product_description = ' '.join(product_description.split())

        return product_description

    def _build_product_search_url(self, product_description: str) -> str:
        product_description = self._clean_product_description(
            product_description
        )
        product_description = product_description.replace(' ', '-')

        return f'{self.search_url}/{product_description}'

    async def get_marketplace_id(self, seller_url: str):
        marketplace_id = ''

        try:
            parsed_url = urlparse(seller_url)
            query_params = parse_qs(parsed_url.query)
            marketplace_id = query_params.get('item_id', [None])[0]
        except Exception as e:
            raise MercadoLibreScraperException(
                f'Error while getting product ID: {e}'
            )

        return marketplace_id

    async def get_brand(self):
        brand = ''

        try:
            brand_xpath_expression = (
                "//span[contains(text(), 'Marca:')]/following-sibling::span"
            )
            brand = self.webdriver.find_element(
                By.XPATH, brand_xpath_expression
            ).text.strip()
        except Exception as e:
            raise MercadoLibreScraperException(
                f'Error while getting product brand: {e}'
            )

        return brand

    async def get_description(self):
        description = ''

        try:
            description = self.webdriver.find_element(
                By.CSS_SELECTOR, 'h1.ui-pdp-title'
            ).text
        except Exception as e:
            raise MercadoLibreScraperException(
                f'Error while getting product description: {e}'
            )

        return description

    def _get_price_cents(self, price_container):
        """Attempt to retrieve the cents part of the price from the price_container."""
        try:
            price_cents = price_container.find_element(
                By.CSS_SELECTOR, 'span.andes-money-amount__cents'
            ).text
            return price_cents
        except NoSuchElementException:
            return ''

    async def get_price(self):
        price = ''

        try:
            price_container = self.webdriver.find_element(
                By.CSS_SELECTOR, 'span.andes-money-amount.ui-pdp-price__part'
            )
            currency_symbol = price_container.find_element(
                By.CSS_SELECTOR, 'span.andes-money-amount__currency-symbol'
            ).text
            price_fraction = price_container.find_element(
                By.CSS_SELECTOR, 'span.andes-money-amount__fraction'
            ).text
            price_cents = self._get_price_cents(price_container)

            if price_cents:
                price = f'{currency_symbol}{price_fraction},{price_cents}'
            else:
                price = f'{currency_symbol}{price_fraction}'
        except Exception as e:
            raise MercadoLibreScraperException(
                f'Error while getting product price: {e}'
            )

        return price

    async def get_seller_id(self, seller_url: str):
        seller_id = ''

        try:
            parsed_url = urlparse(seller_url)
            query_params = parse_qs(parsed_url.query)
            seller_id = query_params.get('seller_id', [None])[0]
        except Exception as e:
            raise MercadoLibreScraperException(
                f'Error while getting seller ID: {e}'
            )

        return seller_id

    async def get_seller_name(self):
        seller_name = ''

        try:
            seller_name_xpath_expression = (
                "//div[@class='ui-pdp-seller__header']/descendant::span[2]"
            )  
            seller_name = self.webdriver.find_element(
                By.XPATH, seller_name_xpath_expression
            ).text
        except Exception as e:
            raise MercadoLibreScraperException(
                f'Error while getting seller name: {e}'
            )

        return seller_name

    def _find_element_by_multiple_xpaths(self, xpaths):
        """Try to find an element using multiple XPaths, return the first successful one."""
        for xpath in xpaths:
            try:
                element = self.webdriver.find_element(By.XPATH, xpath)
                if element:
                    return element
            except NoSuchElementException:
                continue
        raise NoSuchElementException(
            'Element not found with any of the provided XPaths.'
        )

    async def get_seller_url(self):
        seller_url = ''
        seller_link_xpaths = (
            "//div[@id='seller_info']/descendant::a[1]",
            "//div[@id='seller_data']/descendant::a[1]",
        )

        try:
            seller_link_element = self._find_element_by_multiple_xpaths(
                seller_link_xpaths
            )
            seller_url = seller_link_element.get_attribute('href')
        except Exception as e:
            raise MercadoLibreScraperException(
                f'Error while getting seller URL: {e}'
            )

        return seller_url

    async def get_seller_info(self, seller_product_page: str):
        self.webdriver.get(seller_product_page)
        seller_url = ''

        seller = {
            'product_url': '',
            'marketplace_id': '',
            'brand': '',
            'description': '',
            'price': '',
            'seller_id': '',
            'seller_name': '',
            'seller_url': '',
        }

        try:
            seller_url = await self.get_seller_url()
            seller['product_url'] = seller_product_page
            seller['marketplace_id'] = await self.get_marketplace_id(
                seller_url
            )
            seller['brand'] = await self.get_brand()
            seller['description'] = await self.get_description()
            seller['price'] = await self.get_price()
            seller['seller_id'] = await self.get_seller_id(seller_url)
            seller['seller_name'] = await self.get_seller_name()
            seller['seller_url'] = seller_url
        except MercadoLibreScraperException as e:
            self.logger.error(
                f'Error while getting seller info details from {seller_product_page}: {e}'
            )
        except Exception as e:
            self.logger.error(
                f'Unexpected Error while getting seller info from {seller_product_page}: {e}'
            )

        return seller

    async def get_sellers_list(self):
        sellers = []

        try:
            self.webdriver.get(str(self.product_url))
            product_description = self.webdriver.find_element(
                By.CSS_SELECTOR, 'h1.ui-pdp-title'
            ).text
            product_search_url = self._build_product_search_url(
                product_description
            )
            self.webdriver.get(product_search_url)
            cleaned_description = set(
                self._clean_product_description(product_description).split()
            )
            products_search_result_section = self.webdriver.find_element(
                By.CSS_SELECTOR,
                'section.ui-search-results.ui-search-results--without-disclaimer',
            )
        except Exception as e:
            self.logger.error(f'Error while searching for product: {e}')
            return []

        if products_search_result_section:
            try:
                sellers_urls = products_search_result_section.find_elements(
                    By.CSS_SELECTOR,
                    'a.ui-search-item__group__element.ui-search-link__title-card.ui-search-link',
                )
                for seller_link in sellers_urls:
                    title = (
                        seller_link.get_attribute('title')
                        if seller_link.get_attribute('title')
                        else ''
                    )
                    cleaned_title = set(
                        self._clean_product_description(title).split()
                    )
                    if cleaned_title == cleaned_description:
                        sellers.append(seller_link.get_attribute('href'))
            except Exception as e:
                self.logger.error(f'Error while getting sellers list: {e}')
                return []

        return sellers
