import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.ws_manager import market_ws_manager
from app.cache.redis_client import redis_client

router = APIRouter()

async def redis_listener(websocket: WebSocket):
    """
    Per-connection Redis listener using the synchronous redis-py client.
    Uses get_message in a non-blocking way with asyncio.sleep.
    """
    pubsub = redis_client.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe("market:stream")
    
    try:
        while True:
            # get_message is non-blocking when called without a timeout
            message = pubsub.get_message()
            
            if message and message["type"] == "message":
                data = json.loads(message["data"])
                
                # Get current subscriptions for this specific websocket
                symbols = market_ws_manager.active_connections.get(websocket, set())
                
                if symbols:
                    # Filter symbols
                    filtered = [
                        item
                        for item in data["data"]
                        if item["symbol"] in symbols
                    ]
                    
                    if filtered:
                        try:
                            await websocket.send_json({
                                "type": "market_batch",
                                "data": filtered
                            })
                        except Exception:
                            break # Connection probably closed
            
            # Periodically yield to the event loop
            await asyncio.sleep(0.01)
            
    except Exception as e:
        print(f"Redis listener error for {id(websocket)}: {e}")
    finally:
        pubsub.unsubscribe("market:stream")
        pubsub.close()

@router.websocket("/ws/market")
async def market_ws(websocket: WebSocket):
    await market_ws_manager.connect(websocket)
    
    # Start a background task for this specific connection's Redis listener
    listener_task = asyncio.create_task(redis_listener(websocket))

    try:
        while True:
            # Handle incoming messages (e.g., subscriptions)
            message = await websocket.receive_json()
            if message.get("type") == "subscribe":
                symbols = message.get("symbols", [])
                market_ws_manager.subscribe(websocket, symbols)
                print(f"Connection {id(websocket)} subscribed to {symbols}")
                
    except WebSocketDisconnect:
        market_ws_manager.disconnect(websocket)
    finally:
        # Cancel the redis listener when client disconnects
        listener_task.cancel()
        try:
            await listener_task
        except asyncio.CancelledError:
            pass