from fastapi import APIRouter
from app.cache.redis_client import redis_client

router = APIRouter(prefix="/market", tags=["market"])

@router.get("/tickers/{symbol}")
def get_ticker(symbol: str):

    price = redis_client.get(f"price:{symbol}")

    return {
        "symbol": symbol,
        "price": price
    }
