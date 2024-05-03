import configparser
import json
import os

from pydantic import BaseModel, ConfigDict, Field, model_validator

from kami_pricing_analytics.data_collector.collector import StrategyFactory
from kami_pricing_analytics.data_collector.strategies.base_strategy import (
    BaseStrategy,
)
from kami_pricing_analytics.data_storage.base_storage import BaseStorage
from kami_pricing_analytics.data_storage.storage_factory import (
    StorageFactory,
    StorageModeOptions,
)
from kami_pricing_analytics.schemas.options import StrategyOptions
from kami_pricing_analytics.schemas.pricing_research import PricingResearch


class PricingService(BaseModel):

    strategy_option: int = Field(default=StrategyOptions.WEB_SCRAPING.value)
    strategy: BaseStrategy = Field(default=None)

    store_result: bool = Field(default=False)
    storage_mode: int = Field(default=0)
    storage: BaseStorage = Field(default=None)

    research: PricingResearch = Field(default=None)

    model_config = ConfigDict(
        title='Pricing Service',
        from_attributes=True,
        use_enum_values=True,
        str_strip_whitespace=True,
    )

    @model_validator(mode='after')
    def set_strategy(self):
        self.strategy = StrategyFactory.get_strategy(
            strategy_option=self.strategy_option,
            product_url=str(self.research.url),
        )
        return self

    @model_validator(mode='after')
    def set_storage(self):

        if self.store_result:
            self.storage = StorageFactory.get_mode(mode=self.storage_mode)
        return self

    async def conduct_research(self):
        """Execute the assigned strategy to conduct research and store the results if necessary."""

        result = await self.strategy.execute()

        self.research.update_research_data(result)

    async def store_research(self):
        if self.store_result:
            research_data = self.research.model_dump_json(
                exclude={'model_config'}
            )
            research_data = json.loads(research_data)
            research_data['strategy'] = StrategyOptions(
                self.strategy_option
            ).name
            await self.storage.save(research_data)
