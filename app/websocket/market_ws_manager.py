# manage user website connections
# subscribe to symbol
# broadcast price updatges
from fastapi import WebSocket


class MarketWSManager:

    def __init__(self):
        # websocket → subscribed symbols
        self.active_connections = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[websocket] = set()
        print("Client connected:", len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            del self.active_connections[websocket]
        print("Client disconnected:", len(self.active_connections))

    def subscribe(self, websocket: WebSocket, symbols):
        if websocket in self.active_connections:
            self.active_connections[websocket].update(symbols)
            print("Subscribed:", symbols)

    async def broadcast(self, batch_message):
        for websocket, symbols in self.active_connections.items():
            # if no subscription → send all
            if not symbols:
                await websocket.send_json(batch_message)
                continue

            # filter symbols
            filtered = [
                item
                for item in batch_message["data"]
                if item["symbol"] in symbols
            ]
            if filtered:
                await websocket.send_json({
                    "type": "market_batch",
                    "data": filtered
                })