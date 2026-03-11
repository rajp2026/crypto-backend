import httpx
import asyncio
from typing import List, Dict, Any

from app.core.constants import (
    BINANCE_BASE_URL,
    BINANCE_EXCHANGE_INFO,
    BINANCE_TICKER_PRICE,
    BINANCE_TICKER_24HR
)


class BinanceClient:

    def __init__(self):
        self.base_url = BINANCE_BASE_URL

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=10.0,
            limits=httpx.Limits(
                max_connections=100,
                max_keepalive_connections=20
            )
        )

    async def _request(self, method: str, url: str) -> Dict[str, Any]:
        """
        Generic request handler with retry logic
        """

        retries = 3

        for attempt in range(retries):
            try:

                response = await self.client.request(method, url)

                response.raise_for_status()

                return response.json()

            except httpx.HTTPError as e:

                if attempt == retries - 1:
                    raise e

                await asyncio.sleep(1)

    # ----------------------------------------
    # Exchange Info
    # ----------------------------------------

    async def get_exchange_info(self) -> Dict[str, Any]:

        return await self._request(
            "GET",
            BINANCE_EXCHANGE_INFO
        )

    # ----------------------------------------
    # Ticker Prices
    # ----------------------------------------

    async def get_ticker_prices(self) -> List[Dict]:

        return await self._request(
            "GET",
            BINANCE_TICKER_PRICE
        )

    # ----------------------------------------
    # 24hr Ticker
    # ----------------------------------------

    async def get_24hr_ticker(self) -> List[Dict]:

        return await self._request(
            "GET",
            BINANCE_TICKER_24HR
        )

    # ----------------------------------------
    # Close client
    # ----------------------------------------

    async def close(self):
        await self.client.aclose()