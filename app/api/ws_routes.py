import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.ws_manager import connection_manager
from app.cache.redis_client import redis_client

router = APIRouter()

# Global task reference for the singleton Redis listener
_singleton_redis_task = None


async def singleton_redis_listener():
    """
    Instance-Level Singleton Listener:
    Subscribes to both 'market:stream' and 'candle:stream' Redis channels.
    Distributes messages to the ConnectionManager for local broadcasting.
    """
    print("[Redis] Starting singleton listener for market:stream + candle:stream")
    pubsub = redis_client.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe("market:stream", "candle:stream")

    try:
        while True:
            message = pubsub.get_message()

            if message and message["type"] == "message":
                channel = message["channel"]
                raw_data = message["data"]

                try:
                    data = json.loads(raw_data)

                    if channel == "market:stream":
                        await connection_manager.broadcast_market_batch(data)

                    elif channel == "candle:stream":
                        symbol = data.get("symbol")
                        interval = data.get("interval")
                        candle = data.get("data")
                        if symbol and interval and candle:
                            await connection_manager.broadcast_candle_update(
                                symbol, interval, candle
                            )

                except Exception as ex:
                    print(f"[Redis] Error processing message on {channel}: {ex}")

            await asyncio.sleep(0.01)

    except Exception as e:
        print(f"[Redis] CRITICAL: Singleton listener error: {e}")
    finally:
        pubsub.unsubscribe("market:stream", "candle:stream")
        pubsub.close()
        print("[Redis] Singleton listener stopped.")


def _notify_candle_engine(action: str, symbol: str, interval: str):
    """Publish a control message to the candle engine via Redis."""
    redis_client.publish(
        "candle:control",
        json.dumps({
            "action": action,
            "symbol": symbol,
            "interval": interval
        })
    )


@router.websocket("/ws")
async def unified_ws(websocket: WebSocket):
    global _singleton_redis_task

    # Start the singleton listener if not running
    if _singleton_redis_task is None or _singleton_redis_task.done():
        _singleton_redis_task = asyncio.create_task(singleton_redis_listener())

    await connection_manager.connect(websocket)

    # Start heartbeat for this client
    heartbeat_task = asyncio.create_task(
        connection_manager.heartbeat_loop(websocket)
    )

    try:
        while True:
            message = await websocket.receive_json()
            msg_type = message.get("type")

            if msg_type == "subscribe_market":
                symbols = message.get("symbols", [])
                connection_manager.subscribe_market(websocket, symbols)

            elif msg_type == "subscribe_candle":
                symbol = message.get("symbol", "")
                interval = message.get("interval", "1m")
                connection_manager.subscribe_candle(websocket, symbol, interval)
                # Notify candle engine to start streaming this pair
                _notify_candle_engine("subscribe", symbol, interval)

            elif msg_type == "unsubscribe_candle":
                symbol = message.get("symbol", "")
                interval = message.get("interval", "1m")
                connection_manager.unsubscribe_candle(websocket, symbol, interval)
                # Check if anyone still needs this stream
                key = (symbol, interval)
                if key not in connection_manager.candle_subscribers:
                    _notify_candle_engine("unsubscribe", symbol, interval)

            elif msg_type == "pong":
                connection_manager.handle_pong(websocket)

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
    except Exception as e:
        print(f"[WS] Error for {id(websocket)}: {e}")
        connection_manager.disconnect(websocket)
    finally:
        heartbeat_task.cancel()