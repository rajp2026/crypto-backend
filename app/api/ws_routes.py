import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.ws_manager import market_ws_manager
from app.cache.redis_client import redis_client

router = APIRouter()

# Global task reference for the singleton listener
_singleton_redis_task = None

async def singleton_redis_listener():
    """
    Instance-Level Singleton Listener:
    Subscribes to the single "market:stream" channel once.
    Distributes the batch message to the WS manager for local broadcasting.
    Scales horizontally as each instance handles its own subset of users.
    """
    print("Starting singleton Redis batch listener...")
    pubsub = redis_client.pubsub(ignore_subscribe_messages=True)
    print("Subscribed to market:stream for singleton listener.")
    pubsub.subscribe("market:stream")
    
    try:
        while True:
            # get_message is non-blocking with sleep
            message = pubsub.get_message()
            
            if message and message["type"] == "message":
                # redis-py with decode_responses=True returns strings, not bytes
                raw_data = message["data"]
                try:
                    batch_data = json.loads(raw_data)
                    # Broadcaster handles filtering and delivery to local users
                    await market_ws_manager.broadcast_batch(batch_data)
                    # Debug log to confirm delivery
                    # print(f"Routed batch to {len(market_ws_manager.active_connections)} users.")
                except Exception as ex:
                    print(f"Error processing Redis message: {ex}")
            
            await asyncio.sleep(0.01) # Yield to event loop
            
    except Exception as e:
        print(f"CRITICAL: Singleton Redis listener error: {e}")
    finally:
        pubsub.unsubscribe("market:stream")
        pubsub.close()
        print("Singleton Redis batch listener stopped.")

@router.websocket("/ws/market")
async def market_ws(websocket: WebSocket):
    global _singleton_redis_task
    
    # Start the singleton listener IF it's not already running on this instance
    if _singleton_redis_task is None or _singleton_redis_task.done():
        _singleton_redis_task = asyncio.create_task(singleton_redis_listener())
    
    await market_ws_manager.connect(websocket)
    
    try:
        while True:
            # Handle incoming messages (subscriptions)
            message = await websocket.receive_json()
            if message.get("type") == "subscribe":
                symbols = message.get("symbols", [])
                market_ws_manager.set_subscriptions(websocket, symbols)
                
    except WebSocketDisconnect:
        market_ws_manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error for {id(websocket)}: {e}")
        market_ws_manager.disconnect(websocket)