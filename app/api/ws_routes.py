from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.ws_manager import market_ws_manager

router = APIRouter()

@router.websocket("/ws/market")
async def market_ws(websocket: WebSocket):

    await market_ws_manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        market_ws_manager.disconnect(websocket)