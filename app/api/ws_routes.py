from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.ws_manager import market_ws_manager

router = APIRouter()


@router.websocket("/ws/market")
async def market_ws(websocket: WebSocket):

    await market_ws_manager.connect(websocket)

    try:

        while True:

            message = await websocket.receive_json()

            if message["type"] == "subscribe":

                symbols = message["symbols"]

                market_ws_manager.subscribe(websocket, symbols)

    except WebSocketDisconnect:

        market_ws_manager.disconnect(websocket)