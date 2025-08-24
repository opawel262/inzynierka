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
