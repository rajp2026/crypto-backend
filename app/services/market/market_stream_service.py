# receive bainace price updates update teh redis price cahce
# update redies price cache
# broadcast to websocket users


# flow 
# Binance WebSocket
#         ↓
# MarketStreamService
#         ↓
# Redis Pub/Sub
#         ↓
# FastAPI WebSocket Server
#         ↓
# Users
import asyncio
import json
from app.exchanges.binance.binance_ws_client import BinanceWSClient
from app.services.redis.redis_client import redis_client


class MarketStreamService:

    REDIS_PRICE_KEY = "market:prices"
    REDIS_STREAM_CHANNEL = "market:stream"

    def __init__(self):
        self.client = BinanceWSClient(self.handle_message)

    async def handle_message(self, data):

        pipe = redis_client.pipeline()

        batch = []

        for ticker in data:

            symbol = ticker["s"]
            price = ticker["c"]

            pipe.hset(
                self.REDIS_PRICE_KEY,
                symbol,
                price
            )

            batch.append({
                "symbol": symbol,
                "price": price
            })

        pipe.execute()

        # publish batch to redis pubsub
        redis_client.publish(
            self.REDIS_STREAM_CHANNEL,
            json.dumps({
                "type": "market_batch",
                "data": batch
            })
        )

    async def start(self):

        print("Starting Market Stream Service...")

        await self.client.connect()