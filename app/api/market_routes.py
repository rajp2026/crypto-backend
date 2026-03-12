from fastapi import APIRouter
from app.cache.redis_client import redis_client
from app.services.market.market_ticker_service import MarketTickerService


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