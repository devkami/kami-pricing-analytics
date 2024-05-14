from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel


class StorageModeOptions(Enum):
    """
    Enumeration of supported storage modes.

    Attributes:
        SQLITE (int): SQLite database mode.
        POSTGRESQL (int): PostgreSQL database mode.
        MYSQL (int): MySQL database mode.
        SQLSERVER (int): SQL Server database mode.
        PLSQL (int): PL/SQL database mode.
    """

    SQLITE = 0
    POSTGRESQL = 1
    MYSQL = 2
    SQLSERVER = 3
    PLSQL = 4


class BaseStorage(BaseModel, ABC):
    """
    Abstract base class for storage operations, providing a template for CRUD operations that all storage implementations must support. This ensures a uniform interface for storage interactions across different backends.

    Methods:
        save(Dict[str, Any]) -> Any: Asynchronously saves data to the storage.
        retrieve(Dict[str, Any]) -> Any: Asynchronously retrieves data from the storage based on specified criteria.
        update(Dict[str, Any], Dict[str, Any]) -> Any: Asynchronously updates data in the storage that matches the specified criteria.
        delete(Dict[str, Any]) -> Any: Asynchronously deletes data from the storage that matches the specified criteria.
    """

    @abstractmethod
    async def save(self, data: Dict[str, Any]) -> Any:
        """
        Abstract method to save data to the storage system.

        Args:
            data (Dict[str, Any]): The data to be saved.

        Returns:
            Any: The result of the save operation, potentially including details such as an identifier or the saved item itself.
        """
        pass

    @abstractmethod
    async def retrieve(self, criteria: Dict[str, Any]) -> Any:
        """
        Abstract method to retrieve data from the storage system based on specified criteria.

        Args:
            criteria (Dict[str, Any]): The criteria used to filter the retrieval.

        Returns:
            Any: The data retrieved from the storage system.
        """
        pass

    @abstractmethod
    async def update(
        self, criteria: Dict[str, Any], data: Dict[str, Any]
    ) -> Any:
        """
        Abstract method to update data in the storage system that matches the specified criteria.

        Args:
            criteria (Dict[str, Any]): The criteria for selecting which data to update.
            data (Dict[str, Any]): The new data to be updated.

        Returns:
            Any: The result of the update operation.
        """
        pass

    @abstractmethod
    async def delete(self, criteria: Dict[str, Any]) -> Any:
        """
        Abstract method to delete data from the storage system that matches the specified criteria.

        Args:
            criteria (Dict[str, Any]): The criteria for selecting which data to delete.

        Returns:
            Any: The result of the delete operation.
        """
        pass
