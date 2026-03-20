from app.websocket.connection_manager import ConnectionManager

connection_manager = ConnectionManager()
print(f"ConnectionManager initialized at {id(connection_manager)}")