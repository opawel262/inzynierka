# gpw_repository.py
from app.domain.portfolio.models import Crypto, CryptoHistoricalPrice, CurrencyPairRate
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime


def update_model(model: Crypto, data: dict) -> Crypto:
    for key, value in data.items():
        if hasattr(model, key):
            setattr(model, key, value)
    return model


class CurrencyPairRateRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_currency_pair_rate_by_quote_and_base(
        self, quote_currency: str, base_currency: str
    ) -> CurrencyPairRate | None:
        return (
            self.db.query(CurrencyPairRate)
            .filter(
                CurrencyPairRate.quote_currency.ilike(quote_currency),
                CurrencyPairRate.base_currency.ilike(base_currency),
            )
            .first()
        )

    def create_currency_pair_rate(
        self, currency_pair_rate_data: Dict
    ) -> CurrencyPairRate:
        currency_pair_rate = CurrencyPairRate(**currency_pair_rate_data)
        self.db.add(currency_pair_rate)
        self.db.commit()
        self.db.refresh(currency_pair_rate)

        return currency_pair_rate

    def get_all_currency_pair_rates(self) -> List[CurrencyPairRate]:
        return self.db.query(CurrencyPairRate).all()

    def update_currency_pair_rate(self, update_data: Dict) -> CurrencyPairRate:
        existing_currency_pair_rate = self.get_currency_pair_rate_by_quote_and_base(
            update_data["quote_currency"], update_data["base_currency"]
        )
        if not existing_currency_pair_rate:
            raise ValueError(
                f"Currency pair {update_data['quote_currency']}/{update_data['base_currency']} does not exist."
            )
        for key, value in update_data.items():
            setattr(existing_currency_pair_rate, key, value)

        self.db.commit()
        self.db.refresh(existing_currency_pair_rate)

        return existing_currency_pair_rate
