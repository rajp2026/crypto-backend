"""
Candle Stream Service — The Candle Engine.

Receives raw kline events from Binance, normalizes them,
stores in Redis sorted sets, and publishes to Redis pub/sub.

Also listens for control messages via 'candle:control' channel
to dynamically subscribe/unsubscribe from Binance kline streams.
"""

import asyncio
import json
from app.exchanges.binance.binance_kline_ws import BinanceKlineWS
from app.cache.redis_client import redis_client


class CandleStreamService:

    REDIS_CANDLE_PREFIX = "candle"      # candle:BTCUSDT:1m
    REDIS_STREAM_CHANNEL = "candle:stream"
    REDIS_CONTROL_CHANNEL = "candle:control"
    MAX_CANDLES_STORED = 1500           # per symbol:interval

    def __init__(self):
        self.kline_ws = BinanceKlineWS(self.handle_kline)

    async def handle_kline(self, data: dict):
        """
        Process a raw Binance kline event.

        Example payload:
        {
          "e": "kline",
          "s": "BTCUSDT",
          "k": {
            "t": 1672515780000,  // kline start time
            "T": 1672515839999,  // kline close time
            "s": "BTCUSDT",
            "i": "1m",
            "o": "23500.00",
            "h": "23510.00",
            "l": "23490.00",
            "c": "23505.00",
            "v": "12.345",
            "x": false  // is this kline closed?
          }
        }
        """
        if data.get("e") != "kline":
            return

        k = data.get("k", {})
        symbol = k.get("s", "")
        interval = k.get("i", "")

        if not symbol or not interval:
            return

        candle = {
            "time": int(k["t"]) // 1000,   # seconds timestamp
            "open": float(k["o"]),
            "high": float(k["h"]),
            "low": float(k["l"]),
            "close": float(k["c"]),
            "volume": float(k.get("v", 0)),
            "closed": k.get("x", False)
        }

        # Store in Redis sorted set (score = timestamp)
        redis_key = f"{self.REDIS_CANDLE_PREFIX}:{symbol}:{interval}"
        redis_client.zadd(
            redis_key,
            {json.dumps(candle): candle["time"]}
        )

        # Trim to keep only recent candles
        total = redis_client.zcard(redis_key)
        if total > self.MAX_CANDLES_STORED:
            redis_client.zremrangebyrank(
                redis_key, 0, total - self.MAX_CANDLES_STORED - 1
            )

        # Publish to candle stream channel
        redis_client.publish(
            self.REDIS_STREAM_CHANNEL,
            json.dumps({
                "type": "candle_update",
                "symbol": symbol,
                "interval": interval,
                "data": candle
            })
        )

    async def _control_listener(self):
        """
        Listen for control messages from FastAPI instances.
        Messages: {"action": "subscribe/unsubscribe", "symbol": "...", "interval": "..."}
        """
        print("[CandleEngine] Starting control listener on candle:control")
        pubsub = redis_client.pubsub(ignore_subscribe_messages=True)
        pubsub.subscribe(self.REDIS_CONTROL_CHANNEL)

        try:
            while True:
                message = pubsub.get_message()
                if message and message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        action = data.get("action")
                        symbol = data.get("symbol", "")
                        interval = data.get("interval", "1m")

                        if action == "subscribe" and symbol:
                            await self.kline_ws.subscribe(symbol, interval)
                        elif action == "unsubscribe" and symbol:
                            await self.kline_ws.unsubscribe(symbol, interval)

                    except Exception as ex:
                        print(f"[CandleEngine] Control message error: {ex}")

                await asyncio.sleep(0.05)
        except Exception as e:
            print(f"[CandleEngine] Control listener error: {e}")
        finally:
            pubsub.unsubscribe(self.REDIS_CONTROL_CHANNEL)
            pubsub.close()

    async def start(self):
        """Start the candle engine — kline WS + control listener."""
        print("[CandleEngine] Starting Candle Stream Service...")

        # Run both concurrently
        await asyncio.gather(
            self.kline_ws.connect(),
            self._control_listener()
        )
