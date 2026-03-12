# manage user website connections
# subscribe to symbol
# broadcast price updatges

from fastapi import WebSocket
from typing import List


class MarketWSManager:

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):

        await websocket.accept()
        self.active_connections.append(websocket)

        print("Client connected:", len(self.active_connections))

    def disconnect(self, websocket: WebSocket):

        self.active_connections.remove(websocket)

        print("Client disconnected:", len(self.active_connections))

    async def broadcast(self, message: dict):
        print("Broadcasting to:", len(self.active_connections))

        for connection in self.active_connections:
            await connection.send_json(message)