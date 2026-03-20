import asyncio
import json
import websockets


async def test():
    async with websockets.connect("ws://localhost:8000/ws") as ws:
        print("Connected to /ws")

        # Test 1: subscribe_market
        await ws.send(json.dumps({"type": "subscribe_market", "symbols": ["BTCUSDT", "ETHUSDT"]}))
        print("Sent subscribe_market")

        # Test 2: subscribe_candle
        await ws.send(json.dumps({"type": "subscribe_candle", "symbol": "BTCUSDT", "interval": "1m"}))
        print("Sent subscribe_candle")

        # Receive some messages
        for i in range(5):
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=10)
                data = json.loads(msg)
                msg_type = data.get("type")
                if msg_type == "market_batch":
                    count = len(data.get("data", []))
                    print(f"  [{i}] market_batch: {count} items")
                elif msg_type == "candle_update":
                    candle = data.get("data", {})
                    print(f"  [{i}] candle_update: {data['symbol']}@{data['interval']} close={candle.get('close')}")
                elif msg_type == "ping":
                    print(f"  [{i}] ping (heartbeat)")
                    await ws.send(json.dumps({"type": "pong"}))
                else:
                    print(f"  [{i}] unknown: {msg_type}")
            except asyncio.TimeoutError:
                print(f"  [{i}] timeout (no message in 10s)")

        print("\nTest passed!")


if __name__ == "__main__":
    asyncio.run(test())
