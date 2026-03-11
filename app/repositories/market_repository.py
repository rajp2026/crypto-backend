from sqlalchemy.orm import Session

from app.models.market_pair import MarketPair


class MarketRepository:

    def get_by_symbol(self, db: Session, symbol: str):

        return db.query(MarketPair).filter(
            MarketPair.symbol == symbol
        ).first()

    def create_pair(
        self,
        db: Session,
        symbol: str,
        base_coin_id,
        quote_coin_id
    ):

        pair = MarketPair(
            symbol=symbol,
            base_coin_id=base_coin_id,
            quote_coin_id=quote_coin_id
        )

        db.add(pair)

        return pair