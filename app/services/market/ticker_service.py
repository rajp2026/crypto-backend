from app.exchanges.binance.binance_client import BinanceClient
from app.cache.redis_client import redis_client


class TickerService:

    def __init__(self):
        self.client = BinanceClient()

    async def sync_prices(self):

        tickers = await self.client.get_ticker_prices()

        pipe = redis_client.pipeline()

        for ticker in tickers:

            symbol = ticker["symbol"]
            price = ticker["price"]

            pipe.hset(
                "market:prices",
                symbol,
                price
            )

        pipe.execute()