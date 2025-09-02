from typing import List, Dict, Any
from fastapi import HTTPException, status
from app.domain.portfolio.repositories.currency_repository import (
    CurrencyPairRateRepository,
)
from app.domain.portfolio.models import Stock, StockHistoricalPrice
from app.domain.portfolio.fetchers.currency_exchange_fetcher import (
    ExchangerateCurrencyRateFetcher,
)


class ExchangeRateCurrencyService:
    def __init__(
        self,
        fetcher: ExchangerateCurrencyRateFetcher,
        repository: CurrencyPairRateRepository,
    ):
        self.fetcher = fetcher
        self.repository = repository

    def fetch_and_save_currency_pair_rate(self):
        rates = self.fetcher.fetch_rates()
        for key, value in rates.items():
            base_currency = key[0:3]  # key example is "USDPLN=X"
            quote_currency = key[3:6]
            rate = value

            currency_pair_rates_data = {
                "base_currency": base_currency,
                "quote_currency": quote_currency,
                "rate": round(float(rate), 4),
            }

            try:
                currency_pair_rate = (
                    self.repository.get_currency_pair_rate_by_quote_and_base(
                        quote_currency=quote_currency, base_currency=base_currency
                    )
                )

                if currency_pair_rate:
                    self.repository.update_currency_pair_rate(currency_pair_rates_data)
                else:
                    self.repository.create_currency_pair_rate(currency_pair_rates_data)

            except Exception as e:
                print(f"Error fetching currency rates: {str(e)}")
        return rates
