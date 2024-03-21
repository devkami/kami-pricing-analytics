from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class PricingResearchModel(Base):
    __tablename__ = 'pricing_research'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sku = Column(String, index=True, nullable=True)
    description = Column(String, nullable=True)
    url = Column(String, nullable=False)
    strategy = Column(String, nullable=False)
    conducted_at = Column(
        DateTime, default=lambda: datetime.now(tz=timezone.utc)
    )
    result = Column(JSON)

    def __repr__(self):
        return f"<PricingResearchModel(id={self.id}, url='{self.url}', strategy='{self.strategy}')>"
