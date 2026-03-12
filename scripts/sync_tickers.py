import asyncio
from app.services.market.market_sync_service import MarketSyncService


async def main():
    service = MarketSyncService()

    await service.sync_24hr_tickers()

    print("Tickers synced successfully")


if __name__ == "__main__":
    asyncio.run(main())