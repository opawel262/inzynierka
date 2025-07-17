# gpw_repository.py
from app.domain.portfolio.models import Crypto, CryptoHistoricalPrice
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime


def update_model(model: Crypto, data: dict) -> Crypto:
    for key, value in data.items():
        if hasattr(model, key):
            setattr(model, key, value)
    return model


class CryptoRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_crypto(self, crypto_data: Dict) -> Crypto:
        crypto = Crypto(**crypto_data)
        self.db.add(crypto)
        self.db.commit()
        self.db.refresh(crypto)

        return crypto

    def get_all_crypto(self) -> List[Crypto]:
        return self.db.query(Crypto).all()

    def update_crypto(self, update_data: Dict) -> Crypto:
        existing_crypto = self.get_crypto_by_symbol(update_data["symbol"])
        if not existing_crypto:
            raise ValueError(
                f"Crypto with symbol {update_data['symbol']} does not exist."
            )
        for key, value in update_data.items():
            setattr(existing_crypto, key, value)

        self.db.commit()
        self.db.refresh(existing_crypto)

        return existing_crypto

    def get_crypto_by_symbol(self, symbol: str) -> Crypto | None:
        return self.db.query(Crypto).filter(Crypto.symbol == symbol).first()

    def create_crypto_historical_price(
        self, crypto: Crypto, historical_price_data: Dict
    ):
        historical_price = CryptoHistoricalPrice(**historical_price_data)
        crypto.historical_prices.append(historical_price)
        self.db.add(historical_price)
        self.db.commit()
        self.db.refresh(historical_price)

        return historical_price

    def update_crypto_historical_price(
        self, historical_price: CryptoHistoricalPrice, update_data: Dict
    ) -> CryptoHistoricalPrice:
        for key, value in update_data.items():
            setattr(historical_price, key, value)
        self.db.commit()
        self.db.refresh(historical_price)

        return historical_price

    def get_crypto_historical_prices_by_symbol_period(
        self, symbol: str, period: str
    ) -> List[CryptoHistoricalPrice]:
        return (
            self.db.query(CryptoHistoricalPrice)
            .join(Crypto)
            .filter(Crypto.symbol == symbol, CryptoHistoricalPrice.period == period)
            .all()
        )

    def get_all_crypto_symbols(self):
        return [crypto.symbol for crypto in db.query(Crypto).all()]
