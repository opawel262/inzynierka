import requests
import time
from typing import Dict, List
import yfinance as yf


class ExchangerateCurrencyRateFetcher:
    BASE_URL = "https://api.exchangerate.host/latest"

    def __init__(self, base_currency: str = "PLN", symbols: List[str] = None):
        self.base_currency = base_currency.upper()
        self.symbols = symbols or [
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

    def fetch_rates(self) -> Dict[str, float]:

        pairs = [
            f"{currency_symbol}{self.base_currency}=X"
            for currency_symbol in self.symbols
        ]
        rates = {}
        try:
            for pair in pairs:
                ticker = yf.Ticker(pair)
                data = ticker.history(period="1d")  # dane z ostatniego dnia
                if not data.empty:
                    close_price = data["Close"].iloc[-1]  # poprawka tutaj
                    rates.update({pair: close_price})
            return rates

        except requests.RequestException as e:
            return {}


ex_c_fetcher = ExchangerateCurrencyRateFetcher()

ex_c_fetcher.fetch_rates()
