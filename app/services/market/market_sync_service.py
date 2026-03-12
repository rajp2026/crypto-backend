from app.exchanges.binance.binance_client import BinanceClient
from app.services.market.market_ticker_service import MarketTickerService


class MarketSyncService:

    def __init__(self):
        self.client = BinanceClient()

    async def sync_24hr_tickers(self):

        tickers = await self.client.get_24hr_ticker()
        for ticker in tickers:

            symbol = ticker["symbol"]

            ticker_data = {
                "price": float(ticker["lastPrice"]),
                "change_24h": float(ticker["priceChangePercent"]),
                "volume_24h": float(ticker["volume"]),
                "high_24h": float(ticker["highPrice"]),
                "low_24h": float(ticker["lowPrice"]),
            }

            MarketTickerService.update_ticker(
                symbol,
                ticker_data
            )

    # instead of above if use bulk update in service layer we can use below function
    # async def sync_24hr_tickers(self):

    # print("Fetching tickers from Binance...")

    # tickers = await self.client.get_24hr_ticker()

    # print("Total tickers:", len(tickers))

    # ticker_map = {}

    # for ticker in tickers:

    #     symbol = ticker["symbol"]

    #     ticker_map[symbol] = {
    #         "price": float(ticker["lastPrice"]),
    #         "change_24h": float(ticker["priceChangePercent"]),
    #         "volume_24h": float(ticker["volume"]),
    #         "high_24h": float(ticker["highPrice"]),
    #         "low_24h": float(ticker["lowPrice"]),
    #     }

    # MarketTickerService.bulk_update_tickers(ticker_map)

    # print("Tickers synced to Redis")