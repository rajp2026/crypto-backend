from sqlalchemy.orm import Session

from app.exchanges.binance.binance_client import BinanceClient
from app.exchanges.binance.binance_market import BinanceMarketParser

from app.repositories.coin_repository import CoinRepository
from app.repositories.market_repository import MarketRepository


class MarketService:

    def __init__(self):

        self.client = BinanceClient()
        self.coin_repo = CoinRepository()
        self.market_repo = MarketRepository()

    async def sync_markets(self, db: Session):

        exchange_info = await self.client.get_exchange_info()

        coins = BinanceMarketParser.parse_coins(exchange_info)
        pairs = BinanceMarketParser.parse_market_pairs(exchange_info)
        breakpoint()
        coin_map = {}

        # Insert coins
        for coin_data in coins:

            coin = self.coin_repo.get_by_symbol(
                db,
                coin_data["symbol"]
            )

            if not coin:
                coin = self.coin_repo.create_coin(
                    db,
                    coin_data["symbol"],
                    coin_data["name"]
                )

            coin_map[coin.symbol] = coin

        db.commit()

        # Insert pairs
        for pair in pairs:

            exists = self.market_repo.get_by_symbol(
                db,
                pair["symbol"]
            )

            if exists:
                continue

            base_coin = coin_map[pair["base_symbol"]]
            quote_coin = coin_map[pair["quote_symbol"]]

            self.market_repo.create_pair(
                db,
                pair["symbol"],
                base_coin.id,
                quote_coin.id
            )

        db.commit()