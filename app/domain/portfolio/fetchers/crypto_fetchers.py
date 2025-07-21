import requests
import json
from datetime import datetime
from app.core.config import settings
from typing import List, Dict, Any

# from app.core.config import settings


### Fetches actual crypto data from CoinGecko API
class CoinGeckoCryptoFetcher:
    """
    CoinGeckoCryptoFetcher is a class for fetching current cryptocurrency market data from the CoinGecko API.
    """

    def __init__(self, currency: str = "pln", per_page: int = 250, page: int = 1):

        self.url = "https://api.coingecko.com/api/v3/coins/markets"
        self.params = {
            "vs_currency": currency,
            "order": "market_cap_desc",
            "per_page": per_page,
            "page": page,
            "sparkline": "false",
            "price_change_percentage": "1h,24h,7d",
        }
        self.headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": settings.COINGECKO_API_KEY,
        }

    def fetch_data(self):
        try:
            response = requests.get(self.url, headers=self.headers, params=self.params)
            response.raise_for_status()
            data = response.json()

            edited_data = [
                {
                    "symbol": item["symbol"],
                    "name": item["name"],
                    "price": item["current_price"],
                    "currency": "PLN",
                    "market_cap": item["market_cap"],
                    "price_change_percentage_1h": round(
                        item.get("price_change_percentage_1h_in_currency", 0) or 0, 2
                    ),
                    "price_change_percentage_24h": round(
                        item.get("price_change_percentage_24h_in_currency", 0) or 0, 2
                    ),
                    "price_change_percentage_7d": round(
                        item.get("price_change_percentage_7d_in_currency", 0) or 0, 2
                    ),
                    "volume_24h": (
                        round(item["total_volume"], 2)
                        if item.get("total_volume") is not None
                        else None
                    ),
                    "volume_24h": item["total_volume"],
                    "circulating_supply": item["circulating_supply"],
                    "icon": item["image"],
                    "market_cap_rank": item["market_cap_rank"],
                    "total_supply": item.get("total_supply"),
                    "max_supply": item.get("max_supply"),
                }
                for item in data
            ]
            return edited_data
        except requests.RequestException as e:
            return None


class BinanaceCryptoFetcher:
    def __init__(
        self,
    ):
        self.params = {}
        self.url = "https://api.binance.com/api/v1/klines"
        self.intervals = ["1m", "1h", "1d", "1w"]  # for zip
        self.periods = ["1h", "1d", "1m", "1y"]  # for zip
        self.limits = [60, 24, 30, 52]  # for zip

    def fetch_historical_crypto_data(self, crypto_symbol):
        formatted_data = []
        try:
            for interval, period, limit in zip(
                self.intervals, self.periods, self.limits
            ):
                params = self.params.copy()
                params.update(
                    {
                        "symbol": f"{crypto_symbol.upper()}USDT",
                        "limit": limit,
                        "interval": interval,
                    }
                )

                response = requests.get(self.url, params=params)
                response.raise_for_status()
                data_list = response.json()

                for data in data_list:
                    new_data = {
                        "date": str(datetime.fromtimestamp(data[0] / 1000)),
                        "open_price": round(float(data[1]), 2),
                        "high_price": round(float(data[2]), 2),
                        "low_price": round(float(data[3]), 2),
                        "close_price": round(float(data[4]), 2),
                        "volume": data[5],
                        "interval": interval,
                        "period": period,
                    }
                    formatted_data.append(new_data)

            return formatted_data
        except requests.RequestException as e:
            print(f"[ERROR] Błąd podczas pobierania danych: {e}")
            return None


# url = "https://api.binance.com/api/v1/klines"
# params = {"symbol": "ALGOUSDT", "interval": "1d", "limit": 100}  # max = 1000
# response = requests.get(url, params=params)
# print(response.json())

# for data in datas:
#     print(f"Czas  otwarcia: {datetime.fromtimestamp(data[0] / 1000)}")
#     print("Cena otwarcia: ", data[1])
#     print("Najwyższa cena: ", data[2])
#     print("Najniższa cena: ", data[3])
#     print("Cena zamknięcia: ", data[4])
#     print("Wolumen: ", data[5])
# print(f"Czas zamknięcia: {datetime.fromtimestamp(data[6] / 1000)}")
