import json
from app.services.redis.redis_client import redis_client


class MarketTickerService:

    REDIS_KEY = "market:tickers"

    @classmethod
    def update_ticker(cls, symbol, ticker_data):

        redis_client.hset(
            cls.REDIS_KEY,
            symbol,
            json.dumps(ticker_data)
        )
    #***** instead of above update_ticker which updates one by one, 
     # ** we can use below function to bulk update 
    #   @classmethod
    # def bulk_update_tickers(cls, tickers):

    #     pipe = redis_client.pipeline()

    #     for symbol, ticker_data in tickers.items():
    #         pipe.hset(
    #             cls.REDIS_KEY,
    #             symbol,
    #             json.dumps(ticker_data)
    #         )

    #     pipe.execute()

    @classmethod
    def get_ticker(cls, symbol):

        data = redis_client.hget(cls.REDIS_KEY, symbol)

        if not data:
            return None

        return json.loads(data)

    @classmethod
    def get_all_tickers(cls):

        data = redis_client.hgetall(cls.REDIS_KEY)

        return {
            symbol: json.loads(value)
            for symbol, value in data.items()
        }