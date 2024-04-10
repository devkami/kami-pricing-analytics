from typing import Dict, Type

from sqlalchemy.orm import DeclarativeMeta

from kami_pricing_analytics.data_storage.modes.sql_storage.database import (
    DatabaseConnection,
)
from kami_pricing_analytics.data_storage.modes.sql_storage.models import (
    PricingResearchModel,
)
from kami_pricing_analytics.data_storage.settings import SQLiteSettings


class SQLiteConnection(DatabaseConnection):
    def __init__(self, settings: SQLiteSettings):
        super().__init__(settings=settings)

    async def save(
        self,
        data: Dict[str, any],
        model: Type[DeclarativeMeta] = PricingResearchModel,
    ) -> any:
        """
        Saves the given data to the database using the specified SQLAlchemy model.

        :param data: The data to be saved.
        :param model: The SQLAlchemy model the data should be saved to.
        :return: The instance of the model that was saved.
        """
        async with self.get_db_session() as session:

            instance = model(**data)
            session.add(instance)
            await session.commit()
            await session.refresh(instance)
            return instance
