from abc import ABC, abstractmethod

from pydantic import BaseModel, HttpUrl


class BaseStrategy(BaseModel, ABC):
    product_url: HttpUrl

    @abstractmethod
    def execute(self) -> dict:
        pass
