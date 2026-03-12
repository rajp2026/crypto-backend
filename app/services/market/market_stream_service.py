# receive bainace price updates update teh redis price cahce
# update redies price cache
# broadcast to websocket users


# flow 
# Binance WS
#      ↓
# Market Stream Service
#      ↓
# Redis update
#      ↓
# WebSocket broadcast

import json
from app.exchanges.binance.binance_ws_client import BinanceWSClient
from app.services.redis.redis_client import redis_client
from app.websocket.ws_manager import market_ws_manager

# market_ws_manager = MarketWSManager()
class MarketStreamService:
    
    REDIS_PRICE_KEY = "market:prices"

    def __init__(self):
        self.client = BinanceWSClient(self.handle_message)

    async def handle_message(self,data):
        print("Received data from Binance:", len(data))
        pipe = redis_client.pipeline()

        for ticker in data:
            symbol = ticker["s"]
            price = ticker["c"]

            pipe.hset(
                self.REDIS_PRICE_KEY,
                symbol,
                price
            )
            # broadcast to users
            await market_ws_manager.broadcast({
                "symbol": symbol,
                "price": price
            })
            print("Broadcasting:", symbol, price)
        pipe.execute()

    async def start(self):
        print("starting market stream service....")
        await self.client.connect()