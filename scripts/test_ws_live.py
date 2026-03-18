import asyncio
import websockets
import json

async def test_ws_stream():
    uri = "ws://localhost:8000/ws/market"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            # Subscribe to BTCUSDT
            subscribe_msg = {
                "type": "subscribe",
                "symbols": ["BTCUSDT", "ETHUSDT"]
            }
            await websocket.send(json.dumps(subscribe_msg))
            print("Sent subscribe message for BTCUSDT, ETHUSDT")
            
            # Listen for 5 messages
            received = 0
            while received < 5:
                # Wait for data
                data = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                msg = json.loads(data)
                if msg.get("type") == "market_batch":
                    batch = msg.get("data", [])
                    symbols = [item["symbol"] for item in batch]
                    print(f"[{received}] Received market_batch with symbols: {symbols}")
                    received += 1
                else:
                    print(f"Received other message: {msg.get('type')}")
            
            print("SUCCESS: Received 5 live update batches!")
            
    except asyncio.TimeoutError:
        print("FAILURE: Timed out waiting for messages (10s).")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_ws_stream())
