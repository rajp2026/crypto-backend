import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.session import SessionLocal
from app.services.market.market_service import MarketService


async def main():

    print("Starting market sync...")

    db = SessionLocal()

    service = MarketService()

    await service.sync_markets(db)

    db.close()

    print("Market sync finished.")


if __name__ == "__main__":
    asyncio.run(main())


