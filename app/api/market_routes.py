from fastapi import APIRouter
from app.cache.redis_client import redis_client
from app.services.market.market_ticker_service import MarketTickerService
import httpx


router = APIRouter(prefix="/market", tags=["market"])

# @router.get("/tickers/{symbol}")
# def get_ticker(symbol: str):

#     price = redis_client.hget("market:prices", symbol)

#     return {
#         "symbol": symbol,
#         "price": price
#     }

# @router.get("/tickers")
# def get_all_tickers():

#     prices = redis_client.hgetall("market:prices")

#     return [
#         {"symbol": symbol, "price": price}
#         for symbol, price in prices.items()
#     ]

@router.get("/tickers")
def get_all_tickers():
    return MarketTickerService.get_all_tickers()


@router.get("/ticker/{symbol}")
def get_ticker(symbol: str):
    return MarketTickerService.get_ticker(symbol)


@router.get("/candles/{symbol}")
async def get_candles(symbol: str, interval: str = "1m", end_time: int | None = None):

    url = "https://api.binance.com/api/v3/klines"

    binance_symbol = symbol.replace("_", "").replace("-", "").upper()

    params = {
        "symbol": binance_symbol,
        "interval": interval,
        "limit": 1000
    }
    if end_time:
        params['endTime'] =  end_time

    async with httpx.AsyncClient() as client:
        res = await client.get(url, params=params)
        data = res.json()
        
    if not isinstance(data, list):
        # E.g. {"code": -1121, "msg": "Invalid symbol."}
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