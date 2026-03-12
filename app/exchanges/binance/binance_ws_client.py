import asyncio
import json
import websockets


BINANCE_WS_URL = "wss://stream.binance.com:9443/ws/!ticker@arr"


class BinanceWSClient:

    def __init__(self, message_handler):
        """
        message_handler → function that processes incoming messages
        """
        self.url = BINANCE_WS_URL
        self.message_handler = message_handler
        self.reconnect_delay = 5

    async def connect(self):

        while True:
            try:
                print("Connecting to Binance WebSocket...")

                async with websockets.connect(self.url) as websocket:

                    print("Connected to Binance WebSocket")

                    await self.listen(websocket)

            except Exception as e:
                print("WebSocket error:", e)
                print(f"Reconnecting in {self.reconnect_delay} seconds...")

                await asyncio.sleep(self.reconnect_delay)

    async def listen(self, websocket):

        async for message in websocket:

            try:
                data = json.loads(message)

                # pass to processing layer
                await self.message_handler(data)

            except Exception as e:
                print("Message processing error:", e)