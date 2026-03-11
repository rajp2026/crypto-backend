from sqlalchemy import Column, String, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database.base import Base


class MarketPair(Base):
    __tablename__ = "market_pairs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    symbol = Column(String, unique=True, index=True, nullable=False)

    base_coin_id = Column(
        UUID(as_uuid=True),
        ForeignKey("coins.id"),
        nullable=False
    )

    quote_coin_id = Column(
        UUID(as_uuid=True),
        ForeignKey("coins.id"),
        nullable=False
    )

    is_active = Column(Boolean, default=True)

    # relationships
    base_coin = relationship(
        "Coin",
        foreign_keys=[base_coin_id],
        back_populates="base_pairs",
        lazy = "joined"
    )

    quote_coin = relationship(
        "Coin",
        foreign_keys=[quote_coin_id],
        back_populates="quote_pairs",
        lazy = 'joined'
    )