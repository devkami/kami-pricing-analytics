import json
import logging
import re
from typing import Any, Dict, List
from urllib.parse import urlparse

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    ValidationError,
    field_validator,
    model_validator,
)

from kami_pricing_analytics.data_collector.collector import StrategyFactory
from kami_pricing_analytics.data_storage.storage_factory import (
    StorageFactory,
    StorageModeOptions,
)
from kami_pricing_analytics.schemas.options import (
    MarketPlaceOptions,
    StrategyOptions,
)


class PricingResearch(BaseModel):

    marketplace: str = Field(default=None)
    sku: str = Field(default=None)
    marketplace_id: str = Field(default=None)
    description: str = Field(default=None)
    brand: str = Field(default=None)
    category: str = Field(default=None)
    url: HttpUrl = Field(default=None)
    sellers: List[Dict] = Field(default=None)
    strategy_name: str = Field(default='web_scraping')

    strategy: Any = Field(default=None)
    result: Dict[str, Any] = Field(default_factory=dict)
    storage: Any = Field(default=None)

    model_config = ConfigDict(
        from_attributes=True, arbitrary_types_allowed=True
    )

    @model_validator(mode='after')
    def ensure_url_or_marketplace(self):
        if not self.url and not (self.marketplace and self.marketplace_id):
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
                    self.marketplace = option.name
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

    @field_validator('strategy_name')
    @classmethod
    def validate_strategy(cls, value):
        if isinstance(value, int):
            strategy_name = StrategyOptions.get_strategy_name(value)
            if strategy_name:
                return strategy_name
            else:
                raise ValueError(
                    f'Invalid strategy option. Available options are: {list(StrategyOptions)}'
                )

    def set_strategy(self, strategy_option: int):
        self.strategy_name = StrategyOptions.get_strategy_name(strategy_option)
        if self.strategy_name:
            self.strategy = StrategyFactory.get_strategy(
                self.strategy_name, str(self.url)
            )
        else:
            raise ValueError(
                f'Invalid strategy option {strategy_option}. Available options are: {list(StrategyOptions)}'
            )

    def update_research_data(self):
        """
        Updates the research data with the result from the strategy execution.
        """
        result = self.result.get('result', [])

        if result:
            self.sellers = result
            first_result = result[0] if result else {}
            self.sku = first_result.get('sku')
            self.description = first_result.get('description')
            self.brand = first_result.get('brand')
            self.category = first_result.get('category')

    async def conduct_research(self):
        self.result = await self.strategy.execute()
        self.update_research_data()

    def set_storage(self, mode_option: StorageModeOptions):
        try:
            self.storage = StorageFactory.get_mode(mode_option)
        except ValueError as e:
            raise ValueError(
                f'Error setting storage mode: {e}. Available options are: {list(StorageModeOptions)}'
            )
        except Exception as e:
            raise ValueError(f'Unexpected error setting storage mode: {e}')

    async def store_research(self):
        """
        Stores the research data using the configured storage object.
        """
        if not self.storage:
            raise ValueError(
                'Storage has not been set for this PricingResearch instance.'
            )

        research_data = self.model_dump_json(
            exclude={'strategy', 'storage', 'result', 'model_config'}
        )
        research_data = json.loads(research_data)
        research_data['strategy'] = research_data.pop('strategy_name')
        logging.info(f'Storing research data: {research_data}')
        await self.storage.save(data=research_data)
