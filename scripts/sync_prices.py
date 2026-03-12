import asyncio

from app.services.market.ticker_service import TickerService


async def price_worker():
    service = TickerService()
    while True:
        await service.sync_prices()
        print("Prices updated")
        await asyncio.sleep(5)
asyncio.run(price_worker())