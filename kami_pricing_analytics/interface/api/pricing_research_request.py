import asyncio
import configparser
import os
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, model_validator

from kami_pricing_analytics.data_collector import CollectorOptions
from kami_pricing_analytics.data_storage import StorageModeOptions
from kami_pricing_analytics.schemas import PricingResearch
from kami_pricing_analytics.services import PricingService

root_folder = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
settings_path = os.path.join('config', 'settings.cfg')
settings = configparser.ConfigParser()
settings.read(settings_path)
storage_mode = StorageModeOptions(settings.getint('storage', 'MODE'))


class PricingResearchRequestException(Exception):
    """
    Custom exception for PricingResearchRequest-realted errors.
    """

    pass


class PricingResearchRequest(BaseModel):
    """
    Handles the construction and submission of pricing research requests.

    Attributes:
        url (Optional[str]): The URL of the product.
        marketplace (Optional[str]): The marketplace name.
        marketplace_id (Optional[str]): The product ID within the marketplace.
        collector_option (int): The scraping strategy to be used.
        store_result (bool): Flag indicating whether to store the research results.
        service (PricingService): An instance of PricingService to execute the research.
    """

    url: Optional[str] = Field(default=None)
    marketplace: Optional[str] = Field(default=None)
    marketplace_id: Optional[str] = Field(default=None)
    collector_option: int = Field(default=CollectorOptions.WEB_SCRAPING.value)
    store_result: bool = Field(default=False)
    service: PricingService = Field(default=None)

    def validate_strategy_option(self) -> 'PricingResearchRequest':
        """
        Validates the strategy option to ensure it is recognized.

        Raises:
            ValueError: If the strategy option is invalid.

        Returns:
            PricingResearchRequest: The instance of this request with a validated strategy.
        """
        if self.collector_option not in CollectorOptions._value2member_map_:
            raise PricingResearchRequestException(
                f'Invalid strategy option {self.collector_option}. Available options are: {list(CollectorOptions)}'
            )
        return self

    def validate_research(self) -> 'PricingResearchRequest':
        """
        Validates the necessary parameters for conducting research.

        Raises:
            ValueError: If neither URL nor marketplace and marketplace_id are provided.

        Returns:
            PricingResearchRequest: The instance of this request with validated research parameters.
        """
        if self.url:
            return self

        if not self.marketplace or not self.marketplace_id:
            raise PricingResearchRequestException(
                'Either Product URL or marketplace and marketplace_id is required to conduct research.'
            )

        return self

    @model_validator(mode='after')
    def validate_input(self) -> 'PricingResearchRequest':
        """
        Performs input validation by checking strategy options and research parameters.

        Returns:
            PricingResearchRequest: The validated request instance.
        """
        try:
            self.validate_strategy_option()
            self.validate_research()
        except ValueError as e:
            raise PricingResearchRequestException(
                f'Value Error while validating input: {e}'
            )
        except Exception as e:
            raise PricingResearchRequestException(
                f'Unexpected error while validating input: {e}'
            )
        return self

    @model_validator(mode='after')
    def get_service_instance(self) -> 'PricingResearchRequest':
        """
        Initializes the PricingService based on the request's parameters.

        Returns:
            PricingResearchRequest: The request instance with an initialized service.
        """
        try:
            research = PricingResearch(
                url=self.url,
                marketplace=self.marketplace,
                marketplace_id=self.marketplace_id,
            )
            self.service = PricingService(
                collector_option=self.collector_option,
                research=research,
                store_result=self.store_result,
                storage_mode=storage_mode,
            )
        except ValueError as e:
            raise PricingResearchRequestException(
                f'Value Error while getting service instance: {e}'
            )
        except Exception as e:
            raise PricingResearchRequestException(
                f'Unexpected error while getting service instance: {e}'
            )
        return self

    async def post(self) -> List[Dict]:
        """
        Submits the pricing research request and optionally stores the results.

        Returns:
            List[Dict]: A list of seller data from the conducted research.

        Raises:
            PricingResearchRequestError: If an error occurs during processing.
        """

        response = []
        try:
            self.validate_input()
            self.service.set_strategy()
            await self.service.conduct_research()

            if self.store_result:
                self.service.set_storage()
                asyncio.create_task(self.service.store_research())

            response = self.service.research.sellers
        except ValueError as e:
            raise ValueError(f'Value Error while processing research: {e}')
        except Exception as e:
            raise ValueError(
                f'Unexpected error while processing research: {e}'
            )

        return response

    async def get(self) -> List[Dict]:
        """
        Retrieves pricing research data or triggers a new research if necessary.

        Returns:
            List[Dict]: A list of seller data from the retrieved or newly conducted research.

        Raises:
            PricingResearchRequestError: If an error occurs during retrieval or processing.
        """

        response = []

        try:
            await self.service.retrieve_research()

            if (
                not self.service.research.sellers
                or self.service.research.expired
            ):
                self.store_result = True
                await self.post()

            reponse = self.service.research.sellers
        except ValueError as e:
            raise PricingResearchRequestException(
                f'Value Error while getting research: {e}'
            )
        except Exception as e:
            raise PricingResearchRequestException(
                f'Unexpected error while getting research: {e}'
            )

        return response
