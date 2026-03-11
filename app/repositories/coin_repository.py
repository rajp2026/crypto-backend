from sqlalchemy.orm import Session

from app.models.coin import Coin


class CoinRepository:

    def get_by_symbol(self, db: Session, symbol: str):

        return db.query(Coin).filter(
            Coin.symbol == symbol
        ).first()

    def create_coin(self, db: Session, symbol: str, name: str):

        coin = Coin(
            symbol=symbol,
            name=name
        )

        db.add(coin)

        return coin

    def get_all(self, db: Session):

        return db.query(Coin).all()