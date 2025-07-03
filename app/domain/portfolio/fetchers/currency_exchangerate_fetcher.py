import requests
import time
from typing import Dict, List


class ExchangerateCurrencyRateFetcher:
    BASE_URL = "https://api.exchangerate.host/latest"

    def __init__(self, base_currency: str = "PLN", symbols: List[str] = None):
        self.base_currency = base_currency.upper()
        self.symbols = symbols or [
            "USD",
            "EUR",
            "GBP",
            "CHF",
            "JPY",
            "CNY",
            "AUD",
            "CAD",
            "SEK",
            "NOK",
            "CZK",
            "HUF",
        ]

    def fetch_rates(self) -> Dict[str, float]:
        params = {"base": self.base_currency, "symbols": ",".join(self.symbols)}

        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("rates", {})
        except requests.RequestException as e:
            print(f"[ERROR] Błąd podczas pobierania danych: {e}")
            return {}

    def print_rates(self, rates: Dict[str, float]):
        print(f"\n💱 Kursy walut względem: {self.base_currency}")
        for currency, rate in sorted(rates.items()):
            print(f"1 {self.base_currency} = {rate:.4f} {currency}")
        print("-" * 40)


