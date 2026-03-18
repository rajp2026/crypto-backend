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
from app.cache.redis_client import redis_client


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
            change = ticker["P"]

            pipe.hset(
                self.REDIS_PRICE_KEY,
                symbol,
                price
            )

            batch.append({
                "symbol": symbol,
                "price": price,
                "change_24h": float(change)
            })

        pipe.execute()

        # Phase 3 Batch Publishing
        # This sends the entire update array in one Redis message.
        # It's then picked up by the Singleton Listener on each FastAPI instance.
        redis_client.publish(
            self.REDIS_STREAM_CHANNEL,
            json.dumps({
                "type": "market_batch",
                "data": batch
            })
        )
        
        print(f"Published batch of {len(batch)} updates to {self.REDIS_STREAM_CHANNEL}")

    async def start(self):

        print("Starting Market Stream Service...")

        await self.client.connect()