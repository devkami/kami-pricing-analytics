import asyncio
import configparser
import os
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from kami_pricing_analytics.data_storage.storage_factory import (
    StorageModeOptions,
)
from kami_pricing_analytics.schemas.options import StrategyOptions
from kami_pricing_analytics.schemas.pricing_research import PricingResearch
from kami_pricing_analytics.services.pricing_service import PricingService

root_folder = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
settings_path = os.path.join('config', 'settings.cfg')
settings = configparser.ConfigParser()
settings.read(settings_path)
storage_mode = StorageModeOptions(settings.getint('storage', 'MODE'))


class PricingResearchRequest(BaseModel):
    url: Optional[str] = Field(default=None)
    marketplace: Optional[str] = Field(default=None)
    marketplace_id: Optional[str] = Field(default=None)
    strategy_option: int = Field(default=StrategyOptions.WEB_SCRAPING.value)
    store_result: bool = Field(default=False)
    service: PricingService = Field(default=None)

    def validate_strategy_option(self):
        if self.strategy_option not in StrategyOptions._value2member_map_:
            raise ValueError(
                f'Invalid strategy option {self.strategy_option}. Available options are: {list(StrategyOptions)}'
            )
        return self

    def validate_research(self):
        if self.url:
            return self

        if not self.marketplace or not self.marketplace_id:
            raise ValueError(
                'Either Product URL or marketplace and marketplace_id is required to conduct research.'
            )

        return self

    @model_validator(mode='after')
    def validate_input(self):
        self.validate_strategy_option()
        self.validate_research()
        return self

    @model_validator(mode='after')
    def get_service_instance(self):
        research = PricingResearch(
            url=self.url,
            marketplace=self.marketplace,
            marketplace_id=self.marketplace_id,
        )
        self.service = PricingService(
            strategy_option=self.strategy_option,
            research=research,
            store_result=self.store_result,
            storage_mode=storage_mode,
        )
        return self

    async def post(self):
        self.validate_input()
        self.service.set_strategy()
        await self.service.conduct_research()

        if self.store_result:
            self.service.set_storage()
            asyncio.create_task(self.service.store_research())

        return self.service.research.sellers
