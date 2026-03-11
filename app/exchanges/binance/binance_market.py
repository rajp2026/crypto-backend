from typing import Dict, List, Tuple


class BinanceMarketParser:

    @staticmethod
    def parse_coins(exchange_info: Dict) -> List[Dict]:
        """
        Extract unique coins from exchange info
        """

        coins = {}

        for symbol_data in exchange_info["symbols"]:

            base = symbol_data["baseAsset"]
            quote = symbol_data["quoteAsset"]

            coins[base] = {
                "symbol": base,
                "name": base
            }

            coins[quote] = {
                "symbol": quote,
                "name": quote
            }

        return list(coins.values())

    @staticmethod
    def parse_market_pairs(exchange_info: Dict) -> List[Dict]:

        pairs = []

        for symbol_data in exchange_info["symbols"]:

            if symbol_data["status"] != "TRADING":
                continue

            pairs.append({
                "symbol": symbol_data["symbol"],
                "base_symbol": symbol_data["baseAsset"],
                "quote_symbol": symbol_data["quoteAsset"]
            })

        return pairs