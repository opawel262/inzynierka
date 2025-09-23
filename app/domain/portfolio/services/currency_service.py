from typing import List
from app.domain.portfolio.models import CurrencyPairRate
from app.domain.portfolio.repositories.currency_repository import (
    CurrencyPairRateRepository,
)


class CurrencyService:
    def __init__(self, repository: CurrencyPairRateRepository):
        self.repository = repository

    def get_currency_pair_rates(self) -> List[CurrencyPairRate]:
        """
        Get all currency pair rates from the repository.
        """
        currency_pair_rates = self.repository.get_all_currency_pair_rates()
        return currency_pair_rates

    def get_all_currencies(self) -> List[CurrencyPairRate]:
        currencies_pair_rate = self.repository.get_all_currency_pair_rates()
        currencies = []
        for currency in currencies_pair_rate:
            currency_dict = {}

            if currency.base_currency == "USD":
                currency_dict["name"] = "Dolar Amerykański"
            elif currency.base_currency == "EUR":
                currency_dict["name"] = "Euro"
            elif currency.base_currency == "GBP":
                currency_dict["name"] = "Funt Brytyjski"
            elif currency.base_currency == "CNY":
                currency_dict["name"] = "Chiński Juan"
            elif currency.base_currency == "JPY":
                currency_dict["name"] = "Jen Japoński"
            elif currency.base_currency == "INR":
                currency_dict["name"] = "Rupia Indyjska"
            elif currency.base_currency == "CAD":
                currency_dict["name"] = "Dolar Kanadyjski"
            elif currency.base_currency == "AUD":
                currency_dict["name"] = "Dolar Australijski"
            elif currency.base_currency == "RUB":
                currency_dict["name"] = "Rubel Rosyjski"
            elif currency.base_currency == "TRY":
                currency_dict["name"] = "Lira Turecka"
            elif currency.base_currency == "SEK":
                currency_dict["name"] = "Korona Szwedzka"
            elif currency.base_currency == "CHF":
                currency_dict["name"] = "Frank Szwajcarski"
            elif currency.base_currency == "ZAR":
                currency_dict["name"] = "Rand Południowoafrykański"

            currency_dict["symbol"] = currency.base_currency
            currency_dict["price"] = currency.rate

            currencies.append(currency_dict)
        currencies.append({"name": "Polski Złoty", "symbol": "PLN", "price": 1.0})
        return currencies
