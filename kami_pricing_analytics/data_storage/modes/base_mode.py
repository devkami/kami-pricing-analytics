from abc import ABC, abstractmethod
from typing import Any, Dict

from pydantic import BaseModel


class BaseMode(BaseModel, ABC):
    """
    Abstract base class defining the contract for storage operations.
    All concrete storage mode implementations should inherit from this class
    and implement its CRUD methods.
    """

    @abstractmethod
    async def save(self, data: Dict[str, Any]) -> Any:
        """
        Save a new item to the storage.

        :param data: The data to be saved.
        :return: The result of the save operation, which could include the saved item or an identifier.
        """
        pass

    @abstractmethod
    async def retrieve(self, criteria: Dict[str, Any]) -> Any:
        """
        Retrieve items from the storage based on the specified criteria.

        :param criteria: The criteria used to filter items.
        :return: The retrieved items.
        """
        pass

    @abstractmethod
    async def update(
        self, criteria: Dict[str, Any], data: Dict[str, Any]
    ) -> Any:
        """
        Update items in the storage that match the specified criteria with the provided data.

        :param criteria: The criteria to select items to be updated.
        :param data: The data for the update.
        :return: The result of the update operation.
        """
        pass

    @abstractmethod
    async def delete(self, criteria: Dict[str, Any]) -> Any:
        """
        Delete items from the storage that match the specified criteria.

        :param criteria: The criteria to select items to be deleted.
        :return: The result of the delete operation.
        """
        pass
