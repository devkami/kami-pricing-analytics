from datetime import datetime, timezone

from sqlalchemy import JSON, Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.types import TIMESTAMP

Base = declarative_base()

class PricingResearchModel(Base):
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

    def __repr__(self):
        return f"<PricingResearchModel(id={self.id}, url='{self.url}', strategy='{self.strategy}')>"
