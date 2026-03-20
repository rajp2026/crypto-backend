import asyncio
import json
import time
from fastapi import WebSocket


class ConnectionManager:
    """
    Unified WebSocket Manager.

    Data structures:
        symbol_subscribers:  symbol → set(websockets)
        candle_subscribers:  (symbol, interval) → set(websockets)
        ws_market_symbols:   websocket → set(symbols)          [reverse index]
        ws_candle_keys:      websocket → set((symbol, interval)) [reverse index]
    """

    HEARTBEAT_INTERVAL = 30  # seconds

    def __init__(self):
        # Forward maps  (used for broadcasting)
        self.symbol_subscribers: dict[str, set[WebSocket]] = {}
        self.candle_subscribers: dict[tuple[str, str], set[WebSocket]] = {}

        # Reverse maps  (used for cleanup on disconnect)
        self.ws_market_symbols: dict[WebSocket, set[str]] = {}
        self.ws_candle_keys: dict[WebSocket, set[tuple[str, str]]] = {}

        # Heartbeat tracking
        self.last_pong: dict[WebSocket, float] = {}

    # ──────────────────────────────────────────────
    # Connection lifecycle
    # ──────────────────────────────────────────────

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.ws_market_symbols[ws] = set()
        self.ws_candle_keys[ws] = set()
        self.last_pong[ws] = time.time()
        print(f"[WS] Client connected: {id(ws)}")

    def disconnect(self, ws: WebSocket):
        # Clean up market subscriptions
        for symbol in self.ws_market_symbols.get(ws, set()):
            subs = self.symbol_subscribers.get(symbol)
            if subs:
                subs.discard(ws)
                if not subs:
                    del self.symbol_subscribers[symbol]

        # Clean up candle subscriptions
        for key in self.ws_candle_keys.get(ws, set()):
            subs = self.candle_subscribers.get(key)
            if subs:
                subs.discard(ws)
                if not subs:
                    del self.candle_subscribers[key]

        self.ws_market_symbols.pop(ws, None)
        self.ws_candle_keys.pop(ws, None)
        self.last_pong.pop(ws, None)
        print(f"[WS] Client disconnected: {id(ws)}")

    @property
    def connection_count(self) -> int:
        return len(self.ws_market_symbols)

    # ──────────────────────────────────────────────
    # Market subscriptions
    # ──────────────────────────────────────────────

    def subscribe_market(self, ws: WebSocket, symbols: list[str]):
        """Replace market subscriptions for this client."""
        # Remove old subscriptions
        old_symbols = self.ws_market_symbols.get(ws, set())
        for sym in old_symbols:
            subs = self.symbol_subscribers.get(sym)
            if subs:
                subs.discard(ws)
                if not subs:
                    del self.symbol_subscribers[sym]

        # Add new subscriptions
        new_symbols = set(symbols)
        for sym in new_symbols:
            if sym not in self.symbol_subscribers:
                self.symbol_subscribers[sym] = set()
            self.symbol_subscribers[sym].add(ws)

        self.ws_market_symbols[ws] = new_symbols
        print(f"[WS] {id(ws)} subscribed to {len(new_symbols)} market symbols")

    # ──────────────────────────────────────────────
    # Candle subscriptions
    # ──────────────────────────────────────────────

    def subscribe_candle(self, ws: WebSocket, symbol: str, interval: str):
        key = (symbol, interval)
        if key not in self.candle_subscribers:
            self.candle_subscribers[key] = set()
        self.candle_subscribers[key].add(ws)

        if ws not in self.ws_candle_keys:
            self.ws_candle_keys[ws] = set()
        self.ws_candle_keys[ws].add(key)
        print(f"[WS] {id(ws)} subscribed candle: {symbol}@{interval}")

    def unsubscribe_candle(self, ws: WebSocket, symbol: str, interval: str):
        key = (symbol, interval)
        subs = self.candle_subscribers.get(key)
        if subs:
            subs.discard(ws)
            if not subs:
                del self.candle_subscribers[key]

        keys = self.ws_candle_keys.get(ws)
        if keys:
            keys.discard(key)
        print(f"[WS] {id(ws)} unsubscribed candle: {symbol}@{interval}")

    def get_active_candle_keys(self) -> set[tuple[str, str]]:
        """Returns all (symbol, interval) pairs with at least one subscriber."""
        return set(self.candle_subscribers.keys())

    # ──────────────────────────────────────────────
    # Broadcasting
    # ──────────────────────────────────────────────

    async def broadcast_market_batch(self, batch_data: dict):
        """
        Receives the full market batch from Redis and sends filtered
        data to each connected user based on their symbol subscriptions.
        """
        items = batch_data.get("data", [])

        # Group by symbol for efficient routing
        symbol_to_items: dict[str, list] = {}
        for item in items:
            sym = item.get("symbol")
            if sym:
                if sym not in symbol_to_items:
                    symbol_to_items[sym] = []
                symbol_to_items[sym].append(item)

        # Collect per-user data
        ws_payloads: dict[WebSocket, list] = {}
        for sym, sym_items in symbol_to_items.items():
            subscribers = self.symbol_subscribers.get(sym, set())
            for ws in subscribers:
                if ws not in ws_payloads:
                    ws_payloads[ws] = []
                ws_payloads[ws].extend(sym_items)

        # Send to each user
        for ws, payload in ws_payloads.items():
            if payload:
                try:
                    await ws.send_json({
                        "type": "market_batch",
                        "data": payload
                    })
                except Exception:
                    pass  # disconnect will handle cleanup

    async def broadcast_candle_update(self, symbol: str, interval: str, candle: dict):
        """
        Send a candle update to all users subscribed to this (symbol, interval).
        """
        key = (symbol, interval)
        subscribers = self.candle_subscribers.get(key, set())

        message = {
            "type": "candle_update",
            "symbol": symbol,
            "interval": interval,
            "data": candle
        }

        for ws in list(subscribers):
            try:
                await ws.send_json(message)
            except Exception:
                pass

    # ──────────────────────────────────────────────
    # Heartbeat
    # ──────────────────────────────────────────────

    async def heartbeat_loop(self, ws: WebSocket):
        """Ping the client periodically. Disconnect if no pong."""
        try:
            while ws in self.ws_market_symbols or ws in self.ws_candle_keys:
                await asyncio.sleep(self.HEARTBEAT_INTERVAL)
                try:
                    await ws.send_json({"type": "ping"})
                except Exception:
                    break

                # Check if client responded to previous ping
                elapsed = time.time() - self.last_pong.get(ws, 0)
                if elapsed > self.HEARTBEAT_INTERVAL * 2:
                    print(f"[WS] {id(ws)} heartbeat timeout, disconnecting")
                    break
        except Exception:
            pass

    def handle_pong(self, ws: WebSocket):
        self.last_pong[ws] = time.time()
