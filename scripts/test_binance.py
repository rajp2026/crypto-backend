import asyncio

from app.exchanges.binance.binance_client import BinanceClient

async def main():

    client = BinanceClient()
    data = await client.get_exchange_info()
    print(len(data["symbols"]))

    await client.close()


asyncio.run(main())