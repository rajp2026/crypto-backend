import asyncio
from app.exchanges.binance.binance_ws_client import BinanceWSClient


async def handle_message(data):

    # print first few updates
    for ticker in data[:5]:
        print(ticker["s"], ticker["c"], ticker["p"], ticker["v"], ticker["h"], ticker["l"])


async def main():

    client = BinanceWSClient(handle_message)

    await client.connect()


if __name__ == "__main__":
    asyncio.run(main())