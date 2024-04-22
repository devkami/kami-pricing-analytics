from urllib.parse import urlparse, parse_qs
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from pydantic import Field
from kami_pricing_analytics.data_collector.strategies.web_scraping.base_scraper import BaseScraper

class MercadoLibreScraper(BaseScraper):
    search_url: str = Field(default='https://lista.mercadolivre.com.br')

    def __init__(self, **data):
        super().__init__(**data)
        self.set_logger('mercado-libre-scraper')

    def _clean_product_description(self, product_description: str) -> str:        
        product_description = product_description.lower()        
        product_description = ''.join(e for e in product_description if e.isalnum() or e.isspace())
        product_description = ' '.join(product_description.split())                

        return product_description
    
    def _build_product_search_url(self, product_description: str) -> str:        
        product_description = self._clean_product_description(product_description)
        product_description = product_description.replace(' ', '-')

        return f'{self.search_url}/{product_description}'
    
    async def get_sellers_url_list(self, product_description: str) -> list:
        product_search_url = self._build_product_search_url(product_description)
        self.webdriver.get(product_search_url)
        cleaned_description = set(self._clean_product_description(product_description).split())
        sellers_url_list = []
        try:
            prodcuts_search_result_section = self.webdriver.find_element(
                By.CSS_SELECTOR,
                'section.ui-search-results.ui-search-results--without-disclaimer'
            )
        except Exception as e:
            self.logger.error(f'Error while searching for product: {e}')
            return []
        
        if prodcuts_search_result_section:
            sellers_urls = prodcuts_search_result_section.find_elements(
                By.CSS_SELECTOR, 
                'a.ui-search-item__group__element.ui-search-link__title-card.ui-search-link'                
            )
            for seller_link in sellers_urls:
                title = seller_link.get_attribute('title') if seller_link.get_attribute('title') else ''
                cleaned_title = set(self._clean_product_description(title).split())
                if cleaned_title == cleaned_description:
                    sellers_url_list.append(seller_link.get_attribute('href'))                    

        return sellers_url_list
    
    def get_seller_id(self, seller_url):
        seller_id = None
        try:
            parsed_url = urlparse(seller_url)
            query_params = parse_qs(parsed_url.query)
            seller_id = query_params.get('seller_id', [None])[0]            
        except Exception as e:
            self.logger.error(f"An error occurred when trying to retrieve seller_id: {e}")
        
        return seller_id
    
    def get_marketplace_id(self, seller_url):
        marketplace_id = None
        try:
            parsed_url = urlparse(seller_url)
            query_params = parse_qs(parsed_url.query)
            marketplace_id = query_params.get('item_id', [None])[0]            
        except Exception as e:
            self.logger.error(f"An error occurred when trying to retrieve marketplace_id: {e}")
        
        return marketplace_id           
    
    
    def get_product_price(self, price_container: WebElement):        
    
        currency_symbol = price_container.find_element(By.CSS_SELECTOR, 'span.andes-money-amount__currency-symbol').text        
        price_fraction = price_container.find_element(By.CSS_SELECTOR, 'span.andes-money-amount__fraction').text        
        price_cents = price_container.find_element(By.CSS_SELECTOR, 'span.andes-money-amount__cents').text
        
        full_price = f"{currency_symbol}{price_fraction},{price_cents}"
    
        return full_price

    async def get_seller_info(self, product: str) -> dict:
        seller_info = {
            'marketplace_id': '',
            'brand':'',
            'description': '',
            'price': '',
            'seller_id': '',
            'seller_name': '',
        }
        self.webdriver.get(product)
        try:
            brand_xpath_expression = "//span[contains(text(), 'Marca:')]/following-sibling::span"
            xpath_expression = "//div[contains(@class, 'ui-seller-info')]/following::a[1]"
            seller_link_element = self.webdriver.find_element(By.XPATH, xpath_expression)
            seller_link = seller_link_element.get_attribute('href')
            price_container = self.webdriver.find_element(By.CSS_SELECTOR, 'span.andes-money-amount.ui-pdp-price__part')
            seller_title = self.webdriver.find_element(By.CSS_SELECTOR, 'div.ui-pdp-seller__header__title')

            seller_info['marketplace_id'] = self.get_marketplace_id(seller_link)
            seller_info['brand'] = self.webdriver.find_element(By.XPATH, brand_xpath_expression).text.strip()
            seller_info['description'] = self.webdriver.find_element(
                By.CSS_SELECTOR, 'h1.ui-pdp-title'
            ).text            
            seller_info['price'] = self.get_product_price(price_container)
            seller_info['seller_id'] = self.get_seller_id(seller_link)
            seller_info['seller_name'] = seller_title.find_element(By.CSS_SELECTOR, 'span.ui-pdp-color--BLUE.ui-pdp-family--REGULAR').text

        except Exception as e:
            self.logger.error(f'Error while getting product description: {e}')
        
        return seller_info

    async def scrap_product(self) -> str:
        await self.set_webdriver()
        self.webdriver.get(str(self.product_url))
        sellers_list = []
        product_description = self.webdriver.find_element(By.CSS_SELECTOR, 'h1.ui-pdp-title').text        
        product_list = await self.get_sellers_url_list(product_description)

        for product in product_list:
            seller_info = await self.get_seller_info(product)
            sellers_list.append(seller_info)

        return sellers_list

    async def execute(self) -> dict:
        return {'result': await self.scrap_product()}