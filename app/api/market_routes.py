from fastapi import APIRouter
from app.services.market.market_ticker_service import MarketTickerService
from app.cache.redis_client import redis_client
import httpx
import json


router = APIRouter(prefix="/market", tags=["market"])


@router.get("/tickers")
def get_all_tickers():
    try:
        return MarketTickerService.get_all_tickers()
    except Exception as e:
        print(f"Error in get_all_tickers: {e}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ticker/{symbol}")
def get_ticker(symbol: str):
    return MarketTickerService.get_ticker(symbol)


@router.get("/candles/{symbol}")
async def get_candles(symbol: str, interval: str = "1m", end_time: int | None = None):

    # Try Redis cache first (only if not requesting historical data)
    if not end_time:
        redis_key = f"candle:{symbol}:{interval}"
        cached = redis_client.zrange(redis_key, 0, -1)
        if cached and len(cached) > 100:
            candles = [json.loads(c) for c in cached]
            # Remove the 'closed' and 'volume' keys for frontend compatibility
            return [
                {
                    "time": c["time"],
                    "open": c["open"],
                    "high": c["high"],
                    "low": c["low"],
                    "close": c["close"],
                }
                for c in candles
            ]

    # Fallback to Binance REST API
    url = "https://api.binance.com/api/v3/klines"

    binance_symbol = symbol.replace("_", "").replace("-", "").upper()

    params = {
        "symbol": binance_symbol,
        "interval": interval,
        "limit": 1000
    }
    if end_time:
        params['endTime'] = end_time

    async with httpx.AsyncClient() as client:
        res = await client.get(url, params=params)
        data = res.json()

    if not isinstance(data, list):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Binance API Error: {data}")

    candles = []

    for c in data:
        candles.append({
            "time": int(c[0] / 1000),
            "open": float(c[1]),
            "high": float(c[2]),
            "low": float(c[3]),
            "close": float(c[4]),
        })

    return candles