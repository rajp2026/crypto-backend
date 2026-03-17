import json
from app.cache.redis_client import redis_client


class MarketTickerService:

    REDIS_KEY = "market:tickers"
    REDIS_PRICE_KEY = "market:prices"


    @classmethod
    def update_ticker(cls, symbol, ticker_data):

        redis_client.hset(
            cls.REDIS_KEY,
            symbol,
            json.dumps(ticker_data)
        )


    # Optional bulk update (good for sync service)
    @classmethod
    def bulk_update_tickers(cls, tickers):

        pipe = redis_client.pipeline()

        for symbol, ticker_data in tickers.items():
            pipe.hset(
                cls.REDIS_KEY,
                symbol,
                json.dumps(ticker_data)
            )

        pipe.execute()


    @classmethod
    def get_ticker(cls, symbol):

        # Sync Redis call
        data = redis_client.hget(cls.REDIS_KEY, symbol)

        if not data:
            return None

        ticker = json.loads(data)

        # override with live price
        live_price = redis_client.hget(cls.REDIS_PRICE_KEY, symbol)

        if live_price:
            ticker["price"] = float(live_price)

        return ticker


    @classmethod
    def get_all_tickers(cls):

        # Sync Redis calls
        tickers = redis_client.hgetall(cls.REDIS_KEY)
        prices = redis_client.hgetall(cls.REDIS_PRICE_KEY)

        result = {}

        for symbol, value in tickers.items():

            ticker = json.loads(value)

            # override with live price
            if symbol in prices:
                ticker["price"] = float(prices[symbol])

            result[symbol] = ticker

        return result