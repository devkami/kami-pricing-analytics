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
from kami_pricing_analytics.schemas.options import StrategyOptions


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

    model_config = ConfigDict(from_attributes=True)

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
