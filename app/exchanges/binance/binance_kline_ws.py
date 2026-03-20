import asyncio
import json
import websockets


BINANCE_WS_BASE = "wss://stream.binance.com:9443/ws"


class BinanceKlineWS:
    """
    Dynamic Binance kline WebSocket client.

    Connects to Binance combined stream endpoint.
    Supports runtime subscribe/unsubscribe for specific symbol@kline_interval.
    """

    def __init__(self, message_handler):
        self.message_handler = message_handler
        self.reconnect_delay = 5
        self._ws = None
        self._active_streams: set[str] = set()  # e.g. {"btcusdt@kline_1m"}
        self._id_counter = 1

    def _make_stream_name(self, symbol: str, interval: str) -> str:
        return f"{symbol.lower()}@kline_{interval}"

    async def connect(self):
        """Connect and listen. Auto-reconnects on failure."""
        while True:
            try:
                print("[Binance Kline] Connecting...")
                async with websockets.connect(BINANCE_WS_BASE) as ws:
                    self._ws = ws
                    print("[Binance Kline] Connected")

                    # Re-subscribe to any active streams (on reconnect)
                    if self._active_streams:
                        await self._send_subscribe(list(self._active_streams))

                    await self._listen(ws)

            except Exception as e:
                print(f"[Binance Kline] Error: {e}")
                print(f"[Binance Kline] Reconnecting in {self.reconnect_delay}s...")
                self._ws = None
                await asyncio.sleep(self.reconnect_delay)

    async def _listen(self, ws):
        async for message in ws:
            try:
                data = json.loads(message)

                # Ignore subscription confirmation messages
                if "result" in data and "id" in data:
                    continue

                await self.message_handler(data)

            except Exception as e:
                print(f"[Binance Kline] Message processing error: {e}")

    async def subscribe(self, symbol: str, interval: str):
        """Subscribe to a kline stream."""
        stream = self._make_stream_name(symbol, interval)
        if stream in self._active_streams:
            return  # already subscribed

        self._active_streams.add(stream)

        if self._ws:
            await self._send_subscribe([stream])
        print(f"[Binance Kline] Subscribed to {stream}")

    async def unsubscribe(self, symbol: str, interval: str):
        """Unsubscribe from a kline stream."""
        stream = self._make_stream_name(symbol, interval)
        if stream not in self._active_streams:
            return

        self._active_streams.discard(stream)

        if self._ws:
            await self._send_unsubscribe([stream])
        print(f"[Binance Kline] Unsubscribed from {stream}")

    async def _send_subscribe(self, streams: list[str]):
        if not self._ws:
            return
        msg = {
            "method": "SUBSCRIBE",
            "params": streams,
            "id": self._id_counter
        }
        self._id_counter += 1
        await self._ws.send(json.dumps(msg))

    async def _send_unsubscribe(self, streams: list[str]):
        if not self._ws:
            return
        msg = {
            "method": "UNSUBSCRIBE",
            "params": streams,
            "id": self._id_counter
        }
        self._id_counter += 1
        await self._ws.send(json.dumps(msg))

    @property
    def active_stream_count(self) -> int:
        return len(self._active_streams)
