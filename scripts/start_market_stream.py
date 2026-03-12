import asyncio
from app.services.market.market_stream_service import MarketStreamService


async def main():

    service = MarketStreamService()

    await service.start()


if __name__ == "__main__":
    asyncio.run(main())