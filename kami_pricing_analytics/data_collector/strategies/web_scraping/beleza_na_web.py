import json

from bs4 import BeautifulSoup

from kami_pricing_analytics.data_collector.strategies.web_scraping.base_scraper import (
    BaseScraper,
)


class BelezaNaWebScraper(BaseScraper):
    async def scrap_product(self) -> str:
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
                'description': row['name'],
                'price': row['price'],
                'seller_name': row['seller']['name'],
            }
            sellers_list.append(seller_info)

        return sellers_list

    async def execute(self) -> dict:
        return {'result': await self.scrap_product()}
