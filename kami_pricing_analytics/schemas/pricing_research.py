import re
from typing import Dict, List, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from kami_pricing_analytics.schemas.options import MarketPlaceOptions


class PricingResearch(BaseModel):

    sku: str = Field(default=None)
    url: Optional[HttpUrl] = Field(default=None)
    marketplace: Optional[str] = Field(default=None)
    marketplace_id: Optional[str] = Field(default=None)
    description: str = Field(default=None)
    brand: str = Field(default=None)
    category: str = Field(default=None)
    sellers: List[Dict] = Field(default=None)

    model_config = ConfigDict(
        title='Pricing Research',
        from_attributes=True,
        use_enum_values=True,
        str_strip_whitespace=True,
    )

    @model_validator(mode='after')
    def ensure_url_or_marketplace(self):
        if self.url:
            return self

        if not self.marketplace or not self.marketplace_id:
            raise ValueError(
                'Either Product URL or marketplace and marketplace_id is required to conduct research.'
            )

        return self

    @model_validator(mode='after')
    def set_url(self):
        if not self.url and (self.marketplace and self.marketplace_id):
            try:
                marketplace_option = MarketPlaceOptions[
                    self.marketplace.upper()
                ]
                self.url = marketplace_option.build_url(self.marketplace_id)
            except KeyError:
                raise ValueError(
                    f'No URL pattern available for marketplace: {self.marketplace}'
                )
            except Exception as e:
                raise ValueError(f'Unexpected error setting URL: {e}')
        return self

    @model_validator(mode='after')
    def extract_marketplace_from_url(self):
        if self.url and not self.marketplace:
            parsed_url = urlparse(str(self.url))
            for option in MarketPlaceOptions:
                marketplace_name = option.name.lower().replace('_', '')
                if marketplace_name in parsed_url.geturl():
                    self.marketplace = option.name.lower()
                    break
        return self

    @model_validator(mode='after')
    def extract_marketplace_id_from_url(self):
        if self.url and not self.marketplace_id:
            url = str(self.url)
            for option in MarketPlaceOptions:
                marketplace_name = option.name.lower().replace('_', '')
                if marketplace_name in url and option.url_pattern:
                    marketplace_id_mask = re.escape(
                        option.url_pattern
                    ).replace(r'\{marketplace_id\}', '(.*)')
                    if marketplace_id_mask:
                        match = re.match(marketplace_id_mask, url)
                        if match:
                            self.marketplace_id = match.group(1)
                            break
        return self

    def update_research_data(self, result: list):
        """
        Updates the research data with the result from the strategy execution.
        """
        if result:
            self.sellers = result
            first_result = result[0] if result else {}
            self.marketplace_id = first_result.get('marketplace_id')
            self.description = first_result.get('description')
            self.brand = first_result.get('brand')
            self.category = first_result.get('category')
