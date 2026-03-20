import asyncio
from app.services.market.candle_stream_service import CandleStreamService


async def main():
    service = CandleStreamService()
    await service.start()


if __name__ == "__main__":
    asyncio.run(main())
