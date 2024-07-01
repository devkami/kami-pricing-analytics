import json
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator

from kami_pricing_analytics.data_collector import (
    BaseCollector,
    CollectorFactory,
    CollectorOptions,
)
from kami_pricing_analytics.data_storage import BaseStorage, StorageFactory
from kami_pricing_analytics.schemas import PricingResearch
from asyncpg.exceptions import DataError

class PricingServiceException(Exception):
    """
    Custom exception class for PricingService-related errors.
    """

    pass


class PricingService(BaseModel):
    """
    Service to manage pricing data research and storage operations, integrating
    strategies for data collection and storage mechanisms.

    Attributes:
        collector_option (int): Identifier for the strategy to use for data collection.
        strategy (BaseCollector): The strategy instance for data collection.
        store_result (bool): Flag to determine if results should be stored.
        storage_mode (int): Identifier for the storage mode to use.
        storage (BaseStorage): The storage instance for data management.
        research (PricingResearch): The research data to process.
    """

    collector_option: int = Field(default=CollectorOptions.WEB_SCRAPING.value)
    strategy: BaseCollector = Field(default=None)

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
    def set_strategy(self) -> 'PricingService':
        """
        Sets the strategy based on the current strategy option and research URL.

        Raises:
            PricingServiceException: If there is an error in setting up the strategy.

        Returns:
            PricingService: The instance of this service with an updated strategy.
        """
        try:
            self.strategy = CollectorFactory.get_strategy(
                collector_option=self.collector_option,
                product_url=str(self.research.url),
            )
        except ValueError as e:
            raise PricingServiceException(
                f'Value Error while setting strategy: {e}'
            )
        except Exception as e:
            raise PricingServiceException(
                f'Unexpected error while setting strategy: {e}'
            )

        return self

    @model_validator(mode='after')
    def set_storage(self) -> 'PricingService':
        """
        Sets the storage mode based on the current storage mode setting and store_result flag.

        Raises:
            PricingServiceException: If there is an error in setting up the storage.

        Returns:
            PricingService: The instance of this service with an updated storage setting.
        """

        try:
            if self.store_result:
                self.storage = StorageFactory.get_mode(mode=self.storage_mode)
        except ValueError as e:
            raise PricingServiceException(
                f'Value Error while setting storage: {e}'
            )
        except Exception as e:
            raise PricingServiceException(
                f'Unexpected error while setting storage: {e}'
            )

        return self

    async def conduct_research(self) -> bool:
        """
        Conducts the research using the assigned strategy and updates the research data.

        Raises:
            PricingServiceException: If there is an error during the research process.

        Returns:
            bool: True if the research was successful, False otherwise.
        """

        is_conducted = False

        try:
            result = await self.strategy.execute()
            self.research.update_research_data(result)
            is_conducted = True
        except ValueError as e:
            raise PricingServiceException(
                f'Value Error while conducting research: {e}'
            )
        except Exception as e:
            raise PricingServiceException(
                f'Unexpected error while conducting research: {e}'
            )

        return is_conducted

    async def store_research(self) -> bool:
        """
        Stores the research data using the configured storage mode if storage is enabled.

        Raises:
            PricingServiceException: If there is an error during the storage process.

        Returns:
            bool: True if the storage was successful, False otherwise.
        """
        is_result_stored = False

        try:
            if self.store_result:
                research_data = self.research.model_dump_json(
                    exclude={'model_config'}
                )
                research_data = json.loads(research_data)
                research_data['strategy'] = CollectorOptions(
                    self.collector_option
                ).name

                # Convert 'conducted_at' to datetime object if it is a string
                if isinstance(research_data['conducted_at'], str):
                    research_data['conducted_at'] = datetime.fromisoformat(research_data['conducted_at'])

                await self.storage.save(research_data)
                is_result_stored = True
        except ValueError as e:
            raise PricingServiceException(
                f'Value Error while storing research: {e}'
            )
        except DataError as e:
            raise PricingServiceException(
                f'Data Error while storing research: {e}'
            )
        except Exception as e:
            raise PricingServiceException(
                f'Unexpected error while storing research: {e}'
            )

        return is_result_stored

    async def retrieve_research(self) -> bool:
        """
        Retrieves the research data based on specified criteria and updates the research attribute.

        Raises:
            PricingServiceException: If there is an error during the retrieval process.

        Returns:
            bool: True if the retrieval was successful, False otherwise.
        """
        is_research_retrieved = False
        try:

            criteria = {
                'marketplace': self.research.marketplace,
                'marketplace_id': self.research.marketplace_id,
            }
            results = await self.storage.retrieve(criteria)
            if results:
                research_data = results[0]
                self.research = PricingResearch(**research_data)
                is_research_retrieved = True
        except ValueError as e:
            raise ValueError(f'Value Error while retrieving research: {e}')
        except Exception as e:
            raise PricingServiceException(
                f'Unexpected error while retrieving research: {e}'
            )

        return is_research_retrieved
