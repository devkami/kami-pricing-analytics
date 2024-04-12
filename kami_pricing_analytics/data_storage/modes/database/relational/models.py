from datetime import datetime, timezone

from sqlalchemy import JSON, Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.types import TIMESTAMP

Base = declarative_base()


class PricingResearchModel(Base):
    __tablename__ = 'pricing_research'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    marketplace = Column(String, nullable=True)
    sku = Column(String, index=True, nullable=True)
    description = Column(String, nullable=True)
    brand = Column(String, nullable=True)
    category = Column(String, nullable=True)
    url = Column(String)
    strategy = Column(String, nullable=True)
    sellers = Column(JSON)

    conducted_at = Column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(tz=timezone.utc)
    )

    def __repr__(self):
        return f"<PricingResearchModel(id={self.id}, url='{self.url}', strategy='{self.strategy}')>"
