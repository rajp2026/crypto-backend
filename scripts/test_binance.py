import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.exchanges.binance.binance_client import BinanceClient

async def main():

    client = BinanceClient()
    data = await client.get_exchange_info()
    print(len(data["symbols"]))

    await client.close()


asyncio.run(main())