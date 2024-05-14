from datetime import datetime, timezone

from sqlalchemy import JSON, Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.types import TIMESTAMP

Base = declarative_base()


class PricingResearchModel(Base):
    """
    Represents a record of pricing research conducted for a product.

    Attributes:
        id (int): The primary key and auto-incremented identifier for each record.
        marketplace (str): The name of the marketplace where the product is listed.
        sku (str): The stock keeping unit of the product.
        marketplace_id (str): The unique identifier of the product within the marketplace.
        description (str): A description of the product.
        brand (str): The brand of the product.
        category (str): The category of the product within the marketplace.
        url (str): The URL of the product on the marketplace website.
        strategy (str): The strategy used for gathering pricing data.
        sellers (JSON): A JSON object containing information about the sellers offering the product.
        conducted_at (datetime): The timestamp when the research was conducted.

    Table name:
        pricing_research
    """

    __tablename__ = 'pricing_research'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    marketplace = Column(String(255), nullable=True)
    sku = Column(String(255), index=True, nullable=True)
    marketplace_id = Column(String(255), nullable=True)
    description = Column(String(1024), nullable=True)
    brand = Column(String(255), nullable=True)
    category = Column(String(255), nullable=True)
    url = Column(String(512), nullable=True)
    strategy = Column(String(255), nullable=True)
    sellers = Column(JSON)

    conducted_at = Column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(tz=timezone.utc)
    )

    def __repr__(self) -> str:
        """
        Provides a simple representation of a pricing research record, which can be useful for debugging.

        Returns:
            str: A string representation of the PricingResearchModel instance.
        """

        return f"<PricingResearchModel(id={self.id}, url='{self.url}', strategy='{self.strategy}')>"
