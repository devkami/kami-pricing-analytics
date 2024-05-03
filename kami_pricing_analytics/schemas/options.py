from enum import Enum


class StrategyOptions(Enum):
    WEB_SCRAPING = 0
    GOOGLE_SHOPPING = 1

    @classmethod
    def get_strategy_name(cls, value):
        strategy_mapping = {
            cls.WEB_SCRAPING.value: 'web_scraping',
            cls.GOOGLE_SHOPPING.value: 'google_shopping',
        }
        return strategy_mapping.get(value, None)


class MarketPlaceOptions(Enum):
    BELEZA_NA_WEB = ('beleza_na_web', None)
    AMAZON = ('amazon', 'https://www.amazon.com.br/dp/{marketplace_id}')
    MERCADO_LIVRE = (
        'mercado_livre',
        'https://produto.mercadolivre.com.br/{marketplace_id}',
    )

    def __init__(self, name, url_pattern):
        self._name = name
        self.url_pattern = url_pattern

    @staticmethod
    def format_mercad_livre_id(marketplace_id):
        if not marketplace_id.startswith('MLB-'):
            if marketplace_id.startswith('MLB'):
                marketplace_id = f'MLB-{marketplace_id[3:]}'
            else:
                marketplace_id = f'MLB-{marketplace_id}'
        return marketplace_id

    def build_url(self, marketplace_id):
        if self.name == 'MERCADO_LIVRE':
            marketplace_id = self.format_mercad_livre_id(
                marketplace_id=marketplace_id
            )
        if self.url_pattern:
            return self.url_pattern.format(marketplace_id=marketplace_id)
