import json
from datetime import datetime, timezone
from typing import Any, Dict, List

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    Json,
    field_validator,
)

from kami_pricing_analytics.data_collector.collector import StrategyFactory
from kami_pricing_analytics.data_storage.repository import StorageFactory
from kami_pricing_analytics.schemas.options import (
    StorageOptions,
    StrategyOptions,
)


class PricingResearch(BaseModel):

    marketplace: str = Field(default=None)
    sku: str = Field(default=None)
    description: str = Field(default=None)
    brand: str = Field(default=None)
    category: str = Field(default=None)
    url: HttpUrl
    sellers: List[Dict] = Field(default=None)    
    strategy_name: str = Field(default='web_scraping')   
    
    strategy: Any = Field(default=None)
    result: Dict[str, Any] = Field(default_factory=dict)
    storage: Any = Field(default=None)
    
    model_config = ConfigDict(
        from_attributes=True, arbitrary_types_allowed=True
    )

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
        if self.result and 'result' in self.result:
            result = self.result['result']
            self.marketplace = str(self.url.host).upper()
            self.sku = result[0].get('sku')
            self.description = result[0].get('description')
            self.brand = result[0].get('brand')
            self.category = result[0].get('category')
            self.url = str(self.url)
            self.sellers = result

    async def conduct_research(self):
        self.result = await self.strategy.execute()
        self.update_research_data()
    
    def set_storage(self, storage_mode_option: int):
        storage_mode_name = StorageOptions.get_storage_mode_name(
            storage_mode_option
        )
        if storage_mode_name:
            self.storage = StorageFactory.get_storage_mode(storage_mode_name)
        else:
            raise ValueError(
                f'Invalid storage mode option {storage_mode_option}. Available options are: {list(StorageOptions)}'
            )

    async def store_research(self):
        """
        Stores the research data using the configured storage object.
        """
        if not self.storage:
            raise ValueError(
                'Storage has not been set for this PricingResearch instance.'
            )

        research_data = self.model_dump_json(exclude= {'strategy', 'storage', 'result', 'model_config'})
        research_data = json.loads(research_data)
        research_data['strategy'] = research_data.pop('strategy_name')

        await self.storage.save(data=research_data)
