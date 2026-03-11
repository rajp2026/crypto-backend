from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database.base import Base


class Coin(Base):
    __tablename__ = "coins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    symbol = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)

    # relationships
    base_pairs = relationship(
        "MarketPair",
        foreign_keys="MarketPair.base_coin_id",
        back_populates="base_coin",
        lazy="selectin"
    )

    quote_pairs = relationship(
        "MarketPair",
        foreign_keys="MarketPair.quote_coin_id",
        back_populates="quote_coin",
        lazy="selectin"
    )