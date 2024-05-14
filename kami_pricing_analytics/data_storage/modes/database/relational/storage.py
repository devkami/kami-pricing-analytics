from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, List, Type

from sqlalchemy import delete, desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeMeta, sessionmaker

from kami_pricing_analytics.data_storage.base_storage import BaseStorage

from .models import PricingResearchModel
from .settings import DatabaseSettings


class DatabaseStorageException(Exception):
    """
    Custom exception class for database storage exceptions.
    """

    pass


class DatabaseStorage(BaseStorage):
    """
    Database storage class that provides methods to interact with the database.

    Attributes:
        _engine (AsyncEngine): The engine to connect to the database.
        _SessionLocal (SessionLocal): The session local class to create a session.
    """

    def __init__(self, settings: DatabaseSettings):
        super().__init__(**settings.model_dump(exclude={'driver'}))

        self._engine = create_async_engine(settings.db_url, echo=True)
        self._SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine,
            class_=AsyncSession,
        )

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Provides a context manager that yields an async database session.

        Yields:
            AsyncSession: The async database session.

        Example:
            async with self.get_session() as session:
                # Do something with the session.
        """
        async with self._SessionLocal() as session:
            yield session

    async def save(
        self,
        data: Dict[str, Any],
        model: Type[DeclarativeMeta] = PricingResearchModel,
    ) -> Any:
        """
        Saves the PricingResearchModel instance to the database.

        Args:
            data (Dict[str, Any]): The data to save.
            model (Type[DeclarativeMeta], optional): The model to save. Defaults to PricingResearchModel.

        Returns:
            Any: The saved instance.

        Raises:
            DatabaseStorageException: If an error occurs while saving the instance.
        """
        try:
            async with self.get_session() as session:
                instance = model(**data)
                session.add(instance)
                await session.commit()
        except Exception as e:
            raise DatabaseStorageException(f'Error while saving instance: {e}')

    async def retrieve(
        self,
        model: Type[DeclarativeMeta] = PricingResearchModel,
        criteria: Dict[str, Any] = {},
    ) -> List[Any]:
        """
        Retrieves the PricingResearchModel instances from the database.

        Args:
            model (Type[DeclarativeMeta], optional): The model to retrieve. Defaults to PricingResearchModel.
            criteria (Dict[str, Any], optional): The criteria to filter the instances. Defaults to {}.

        Returns:
            List[Any]: The retrieved instances.

        Raises:
            DatabaseStorageException: If an error occurs while retrieving the instances.
        """
        results = []
        try:
            async with self.get_session() as session:
                query = (
                    select(model)
                    .filter_by(**criteria)
                    .order_by(desc(model.conducted_at))
                )
                results = await session.execute(query)
                results = results.scalars().all()
        except Exception as e:
            raise DatabaseStorageException(
                f'Error while retrieving instances: {e}'
            )

        return results

    async def update(
        self,
        criteria: Dict[str, Any],
        data: Dict[str, Any],
        model: Type[DeclarativeMeta] = PricingResearchModel,
    ) -> Any:
        """
        Updates the PricingResearchModel instances in the database.

        Args:
            criteria (Dict[str, Any]): The criteria to filter the instances.
            data (Dict[str, Any]): The data to update.
            model (Type[DeclarativeMeta], optional): The model to update. Defaults to PricingResearchModel.

        Returns:
            Any: The updated instance.

        Raises:
            DatabaseStorageException: If an error occurs while updating the instance.
        """

        instance = None
        try:
            async with self.get_session() as session:
                stmt = (
                    update(model)
                    .filter_by(**criteria)
                    .values(**data)
                    .execution_options(synchronize_session='fetch')
                )
                instance = await session.execute(stmt)
                instance = instance.scalars().first()
                await session.commit()
        except Exception as e:
            raise DatabaseStorageException(
                f'Error while updating instance: {e}'
            )

        return instance

    async def delete(
        self,
        criteria: Dict[str, Any],
        model: Type[DeclarativeMeta] = PricingResearchModel,
    ) -> Any:
        """
        Deletes the PricingResearchModel instances from the database.

        Args:
            criteria (Dict[str, Any]): The criteria to filter the instances.
            model (Type[DeclarativeMeta], optional): The model to delete. Defaults to PricingResearchModel.

        Returns:
            Any: The deleted instance.

        Raises:
            DatabaseStorageException: If an error occurs while deleting the instances.
        """
        instance = None
        try:
            async with self.get_session() as session:
                stmt = (
                    delete(model)
                    .filter_by(**criteria)
                    .execution_options(synchronize_session='fetch')
                )
                instance = await session.execute(stmt)
                instance = instance.scalars().first()
                await session.commit()
        except Exception as e:
            raise DatabaseStorageException(
                f'Error while deleting instance: {e}'
            )

        return instance
