import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.market.ticker_service import TickerService


async def main():

    service = TickerService()

    await service.sync_prices()

    print("Prices synced")


asyncio.run(main())