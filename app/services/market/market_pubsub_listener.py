import json
import asyncio
from app.websocket.ws_manager import market_ws_manager
from app.services.redis.redis_client import redis_client


class MarketPubSubListener:

    CHANNEL = "market:stream"

    async def start(self):

        pubsub = redis_client.pubsub()

        pubsub.subscribe(self.CHANNEL)

        print("Subscribed to Redis market stream")

        while True:

            message = pubsub.get_message(ignore_subscribe_messages=True)

            if message:

                data = json.loads(message["data"])

                await market_ws_manager.broadcast(data)

            await asyncio.sleep(0.01)