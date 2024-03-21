from datetime import datetime, timezone
from typing import Any, Dict

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
    id: int = Field(default_factory=int)
    sku: str = Field(default=None)
    description: str = Field(default=None)
    url: HttpUrl
    strategy: str = Field(default='web_scraping')
    conducted_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )
    result: Dict[str, Any] = Field(default_factory=dict)
    storage: Any = Field(default=None)

    model_config = ConfigDict(
        from_attributes=True, arbitrary_types_allowed=True
    )

    @field_validator('strategy')
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
        strategy_name = StrategyOptions.get_strategy_name(strategy_option)
        if strategy_name:
            self.strategy = StrategyFactory.get_strategy(
                strategy_name, str(self.url)
            )
        else:
            raise ValueError(
                f'Invalid strategy option {strategy_option}. Available options are: {list(StrategyOptions)}'
            )

    async def conduct_research(self):
        self.result = await self.strategy.execute()

    def set_storage(self, storage_mode_option: int):
        storage_mode_name = StorageOptions.get_storage_mode_name(
            storage_mode_option
        )
        if storage_mode_name:
            self.storage = StorageFactory.get_storage_mode(
                storage_mode_name, **self.model_config
            )
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

        research_data = {
            'sku': self.sku,
            'description': self.description,
            'url': str(self.url),
            'strategy': self.strategy,
            'conducted_at': self.conducted_at,
            'result': self.result,
        }

        await self.storage.save(data=research_data)
