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


import requests

# Where USD is the base currency you want to use
url = "https://v6.exchangerate-api.com/v6/YOUR-API-KEY/latest/USD"

# Making our request
response = requests.get(url)
data = response.json()

# Your JSON object
print(data)
from forex_python.converter import CurrencyRates

c = CurrencyRates()
rate = c.get_rate("USD", "PLN")
print(f"Kurs USD/PLN: {rate}")
import yfinance as yf

# Lista par walutowych (format: "USDPLN=X" itd.)
BASE = "PLN"
currency_symbols = [
    "USD",  # Dolar amerykański (USA)
    "EUR",  # Euro (strefa euro)
    "CNY",  # Juan chiński (Chiny)
    "JPY",  # Jen japoński (Japonia)
    "GBP",  # Funt szterling (Wielka Brytania)
    "INR",  # Rupia indyjska (Indie)
    "CAD",  # Dolar kanadyjski (Kanada)
    "AUD",  # Dolar australijski (Australia)
    "RUB",  # Rubel rosyjski (Rosja)
    "TRY",  # Lira turecka (Turcja)
    "ZAR",  # Rand południowoafrykański (RPA)
    "SEK",  # Korona szwedzka (Szwecja)
    "CHF",  # Frank szwajcarski (Szwajcaria)
]

pairs = [f"{currency_symbol}{BASE}=X" for currency_symbol in currency_symbols]

for pair in pairs:
    ticker = yf.Ticker(pair)
    data = ticker.history(period="1d")  # dane z ostatniego dnia
    if not data.empty:
        close_price = data["Close"].iloc[-1]  # poprawka tutaj
        print(f"Kurs {pair[:-2]}: {close_price:.4f}")
    else:
        print(f"Brak danych dla {pair}")
