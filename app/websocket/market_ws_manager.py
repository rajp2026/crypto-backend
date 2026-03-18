from fastapi import WebSocket
import json

class MarketWSManager:

    def __init__(self):
        # websocket → set of subscribed symbols
        self.active_connections = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[websocket] = set()
        print(f"Client connected: {id(websocket)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            del self.active_connections[websocket]
        print(f"Client disconnected: {id(websocket)}")

    def set_subscriptions(self, websocket: WebSocket, symbols):
        if websocket in self.active_connections:
            self.active_connections[websocket] = set(symbols)
            print(f"Connection {id(websocket)} watching: {symbols}")

    async def broadcast_batch(self, batch_message: dict):
        """
        Phase 3 Instance-Level Broadcaster:
        Takes the single batch from Redis and delivers it to all local clients.
        Performs per-client symbol filtering before sending.
        """
        for websocket, user_symbols in self.active_connections.items():
            if not user_symbols:
                continue
            
            # Filter batch based on what this specific user is watching
            filtered = [
                item 
                for item in batch_message.get("data", [])
                if item["symbol"] in user_symbols
            ]

            if filtered:
                try:
                    await websocket.send_json({
                        "type": "market_batch",
                        "data": filtered
                    })
                except Exception:
                    # Disconnect handles cleanup
                    pass