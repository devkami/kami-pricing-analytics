from abc import ABC, abstractmethod

from pydantic import BaseModel, HttpUrl


class BaseStrategy(BaseModel, ABC):
    """
    Abstract base class defining a strategy for data collection or processing. This class
    serves as a template for specific strategies that work with products or resources
    identified by URLs.

    Attributes:
        product_url (HttpUrl): The URL of the product or resource that the strategy will work with.

    Methods:
        execute(): Abstract method that must be implemented by subclasses. This method
        is intended to carry out the specific actions of the strategy.
    """

    product_url: HttpUrl
    """The URL of the product or resource the strategy is designed to handle."""

    @abstractmethod
    def execute(self) -> dict:
        """
        Executes the strategy's core logic on the specified product or resource.

        This method should be implemented by subclasses to perform specific actions,
        such as data collection, analysis, or any other process relevant to the
        strategy being implemented.

        Returns:
            dict: The result of the strategy's execution. The structure of the return
            value should be documented by subclasses.
        """
        pass
