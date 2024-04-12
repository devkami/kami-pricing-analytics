from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, List, Type

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeMeta, sessionmaker

from kami_pricing_analytics.data_storage.modes.database.relational.models import (
    PricingResearchModel,
)
from kami_pricing_analytics.data_storage.modes.database.relational.settings import (
    DatabaseSettings,
)
from kami_pricing_analytics.data_storage.storage_base import DataStoreBase


class DatabaseStorage(DataStoreBase):
    def __init__(self, settings: DatabaseSettings):
        super().__init__(**settings.model_dump(exclude={'driver'}))

        self._engine = create_async_engine(settings.url, echo=True)
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
        """
        async with self._SessionLocal() as session:
            yield session

    async def save(
        self,
        data: Dict[str, Any],
        model: Type[DeclarativeMeta] = PricingResearchModel,
    ) -> Any:
        async with self.get_session() as session:
            instance = model(**data)
            session.add(instance)
            await session.commit()
            return instance

    async def retrieve(
        self,
        model: Type[DeclarativeMeta] = PricingResearchModel,
        criteria: Dict[str, Any] = {},
    ) -> List[Any]:
        async with self.get_session() as session:
            query = select(model).filter_by(**criteria)
            result = await session.execute(query)
            return result.scalars().all()

    async def update(
        self,
        criteria: Dict[str, Any],
        data: Dict[str, Any],
        model: Type[DeclarativeMeta] = PricingResearchModel,
    ) -> None:
        async with self.get_session() as session:
            stmt = (
                update(model)
                .filter_by(**criteria)
                .values(**data)
                .execution_options(synchronize_session='fetch')
            )
            await session.execute(stmt)
            await session.commit()

    async def delete(
        self,
        criteria: Dict[str, Any],
        model: Type[DeclarativeMeta] = PricingResearchModel,
    ) -> None:
        async with self.get_session() as session:
            stmt = (
                delete(model)
                .filter_by(**criteria)
                .execution_options(synchronize_session='fetch')
            )
            await session.execute(stmt)
            await session.commit()
