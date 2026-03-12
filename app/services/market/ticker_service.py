"""
Fetch ticker prices from binance
store them in rediss
"""

from app.exchanges.binance.binance_client import BinanceClient
from app.cache.redis_client import redis_client
import json


class TickerService:

    def __init__(self):
        self.client = BinanceClient()

    async def sync_prices(self):

        tickers = await self.client.get_ticker_prices()

        for ticker in tickers:

            symbol = ticker["symbol"]
            price = ticker["price"]

            redis_client.set(
                f"price:{symbol}",
                price
            )