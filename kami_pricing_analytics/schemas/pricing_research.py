import configparser
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from kami_pricing_analytics.data_collector import MarketPlaceOptions

root_folder = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
settings_path = os.path.join('config', 'settings.cfg')
settings = configparser.ConfigParser()
settings.read(settings_path)
update_delay = settings.getint('update', 'DELAY')


class PricingResearchException(Exception):
    """
    Custom exception class for errors related to the PricingResearch operations.
    """

    pass


class PricingResearch(BaseModel):
    """
    Defines the schema for pricing research data, including validation and URL handling.

    Attributes:
        sku (str): Stock Keeping Unit identifier for the product.
        url (Optional[HttpUrl]): Product URL in the marketplace.
        marketplace (Optional[str]): Name of the marketplace.
        marketplace_id (Optional[str]): Unique identifier of the product in the marketplace.
        description (str): Description of the product.
        brand (str): Brand of the product.
        category (str): Product category.
        sellers (List[Dict]): List of sellers offering the product.
        conducted_at (datetime): Timestamp when the research was conducted.
    """

    sku: str = Field(default=None)
    url: Optional[HttpUrl] = Field(default=None)
    marketplace: Optional[str] = Field(default=None)
    marketplace_id: Optional[str] = Field(default=None)
    description: str = Field(default=None)
    brand: str = Field(default=None)
    category: str = Field(default=None)
    sellers: List[Dict] = Field(default=None)
    conducted_at: datetime = Field(default=None)

    model_config = ConfigDict(
        title='Pricing Research',
        from_attributes=True,
        use_enum_values=True,
        str_strip_whitespace=True,
    )

    @model_validator(mode='after')
    def ensure_url_or_marketplace(self) -> 'PricingResearch':
        """
        Validates the presence of either a URL or marketplace and marketplace_id.

        Returns:
            PricingResearch: The instance of the PricingResearch model.

        Raises:
            PricingResearchException: If neither URL nor marketplace and marketplace_id are provided.
        """
        if self.url:
            return self

        if not self.marketplace or not self.marketplace_id:
            raise PricingResearchException(
                'Either Product URL or marketplace and marketplace_id is required to conduct research.'
            )

        return self

    @model_validator(mode='after')
    def set_url(self) -> 'PricingResearch':
        """
        Sets the product URL based on the marketplace and marketplace_id if not provided.

        Returns:
            PricingResearch: The instance of the PricingResearch model.

        Raises:
            PricingResearchException: If unable to set the URL due to missing configuration.
        """
        if not self.url and (self.marketplace and self.marketplace_id):
            try:
                marketplace_option = MarketPlaceOptions[
                    self.marketplace.upper()
                ]
                self.url = marketplace_option.build_url(self.marketplace_id)
            except KeyError:
                raise PricingResearchException(
                    f'No URL pattern available for marketplace: {self.marketplace}'
                )
            except Exception as e:
                raise PricingResearchException(
                    f'Unexpected error setting URL: {e}'
                )
        return self

    @model_validator(mode='after')
    def extract_marketplace_from_url(self) -> 'PricingResearch':
        """
        Extracts and sets the marketplace ID from the URL if not explicitly provided.

        Returns:
            PricingResearch: The instance of the PricingResearch model.

        Raises:
            PricingResearchException: If unable to extract marketplace ID from the URL.
        """
        try:
            if self.url and not self.marketplace:
                parsed_url = urlparse(str(self.url))
                for option in MarketPlaceOptions:
                    marketplace_name = option.name.lower().replace('_', '')
                    if marketplace_name in parsed_url.geturl():
                        self.marketplace = option.name.lower()
                        break
        except Exception as e:
            raise PricingResearchException(
                f'Error while extracting marketplace from URL: {e}'
            )
        return self

    @model_validator(mode='after')
    def extract_marketplace_id_from_url(self) -> 'PricingResearch':
        """
        Extracts and sets the marketplace from the URL if not explicitly provided.

        Returns:
            PricingResearch: The instance of the PricingResearch model.

        Raises:
            PricingResearchException: If unable to extract marketplace ID from the URL.
        """
        try:
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
        except Exception as e:
            raise PricingResearchException(
                f'Error while extracting marketplace ID from URL: {e}'
            )
        return self

    def update_research_data(self, result: list) -> bool:
        """
        Updates the research data with the result from the strategy execution.

        Args:
            result (list): The list of seller data obtained from the strategy execution.

        Returns:
            bool: True if the data was successfully updated, False otherwise.

        Raises:
            PricingResearchException: If an error occurs during the update.
        """

        is_research_updated = False
        try:
            if result:
                self.sellers = result
                first_result = result[0] if result else {}
                self.marketplace_id = first_result.get('marketplace_id')
                self.description = first_result.get('description')
                self.brand = first_result.get('brand')
                self.category = first_result.get('category')
                self.conducted_at = datetime.now(tz=timezone.utc)
                is_research_updated = True
        except Exception as e:
            raise PricingResearchException(
                f'Error while updating research data: {e}'
            )

        return is_research_updated

    @property
    def expired(self) -> bool:
        """
        Determines if the current research data is expired based on the update delay.

        Returns:
            bool: True if the data is expired, False otherwise.
        """

        is_expired = False
        try:
            is_expired = self.conducted_at + timedelta(
                seconds=update_delay
            ) < datetime.now(tz=timezone.utc)
        except Exception as e:
            raise PricingResearchException(
                f'Error while checking if research data is expired: {e}'
            )

        return is_expired
