# gpw_repository.py
from app.domain.portfolio.models import (
    CryptoPortfolio,
    CryptoTransaction,
    Crypto,
    WatchedCryptoInPortfolio,
)
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime


class CryptoPortfolioRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_crypto_portfolio(self, crypto_portfolio_data: Dict) -> CryptoPortfolio:
        crypto_portfolio = CryptoPortfolio(**crypto_portfolio_data)
        self.db.add(crypto_portfolio)
        self.db.commit()
        self.db.refresh(crypto_portfolio)

        return crypto_portfolio

    def get_all_crypto_portfolios(self, user_id: str) -> List[CryptoPortfolio]:
        return (
            self.db.query(CryptoPortfolio)
            .filter(CryptoPortfolio.owner_id == user_id)
            .order_by(CryptoPortfolio.created_at.desc())
            .all()
        )

    def delete_all_crypto_portfolios(self, user_id: str) -> None:
        crypto_portfolios = (
            self.db.query(CryptoPortfolio)
            .filter(CryptoPortfolio.owner_id == user_id)
            .delete()
        )
        if not crypto_portfolios:
            return False
        self.db.commit()
        return True

    def delete_crypto_portfolio_by_id(self, portfolio_id: str) -> None:
        self.db.query(CryptoPortfolio).filter(
            CryptoPortfolio.id == portfolio_id
        ).delete()
        self.db.commit()
        return True

    def get_crypto_portfolio_by_id(self, portfolio_id: str) -> CryptoPortfolio | None:

        return (
            self.db.query(CryptoPortfolio)
            .filter(CryptoPortfolio.id == portfolio_id)
            .first()
        )

    def update_crypto_portfolio(
        self, existing_crypto_portfolio: CryptoPortfolio, update_data: Dict
    ) -> CryptoPortfolio | None:
        for key, value in update_data.items():
            if value is None:
                continue
            setattr(existing_crypto_portfolio, key, value)

        self.db.commit()
        self.db.refresh(existing_crypto_portfolio)

        return existing_crypto_portfolio

    def create_crypto_portfolio_transactions(
        self, crypto_portfolio: CryptoPortfolio, crypto_portfolio_data: Dict
    ):
        transaction = CryptoTransaction(**crypto_portfolio_data)
        crypto_portfolio.transactions.append(transaction)
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(historical_price)

        return historical_price

    def update_crypto_portfolio_transaction(
        self, crypto_portfolio_transaction: CryptoTransaction, update_data: Dict
    ) -> CryptoTransaction:
        for key, value in update_data.items():
            setattr(crypto_portfolio_transaction, key, value)
        self.db.commit()
        self.db.refresh(crypto_portfolio_transaction)

        return crypto_portfolio_transaction

    def get_watched_crypto_in_portfolio_by_id(
        self, portfolio_id: str, crypto_id: str
    ) -> WatchedCryptoInPortfolio | None:
        return (
            self.db.query(WatchedCryptoInPortfolio)
            .filter(
                WatchedCryptoInPortfolio.portfolio_id == portfolio_id,
                WatchedCryptoInPortfolio.crypto_id == crypto_id,
            )
            .first()
        )

    def get_all_watched_crypto_from_portfolio(
        self, portfolio_id: str
    ) -> List[WatchedCryptoInPortfolio]:
        return (
            self.db.query(WatchedCryptoInPortfolio)
            .filter(WatchedCryptoInPortfolio.portfolio_id == portfolio_id)
            .all()
        )

    def add_watched_crypto_to_portfolio(
        self, portfolio_id: str, crypto: Crypto
    ) -> WatchedCryptoInPortfolio:
        watched_crypto = WatchedCryptoInPortfolio(
            portfolio_id=portfolio_id, crypto=crypto
        )
        self.db.add(watched_crypto)
        self.db.commit()
        self.db.refresh(watched_crypto)
        return watched_crypto

    def delete_watched_crypto_from_portfolio(
        self, watched_crypto: WatchedCryptoInPortfolio
    ) -> bool:
        self.db.delete(watched_crypto)
        self.db.commit()
        return True

    def delete_all_watched_cryptos_in_portfolio(self, portfolio_id: str) -> bool:
        watched_cryptos = (
            self.db.query(WatchedCryptoInPortfolio)
            .filter(
                WatchedCryptoInPortfolio.portfolio_id == portfolio_id,
            )
            .all()
        )
        if not watched_cryptos:
            return False
        for watched_crypto in watched_cryptos:
            self.db.delete(watched_crypto)
        self.db.commit()
        return True

    def get_all_transactions_in_crypto_portfolio(
        self,
        portfolio_id: str,
        crypto: Crypto = None,
    ) -> List[CryptoTransaction]:
        query = self.db.query(CryptoTransaction).filter(
            CryptoTransaction.portfolio_id == portfolio_id
        )
        if crypto:
            query = query.filter(CryptoTransaction.crypto == crypto)
        return query.order_by(CryptoTransaction.transaction_date.desc()).all()

    def get_transaction_in_crypto_portfolio_by_id(
        self, portfolio_id: str, transaction_id: str
    ) -> CryptoTransaction | None:
        return (
            self.db.query(CryptoTransaction)
            .filter(
                CryptoTransaction.portfolio_id == portfolio_id,
                CryptoTransaction.id == transaction_id,
            )
            .first()
        )

    def create_transaction_in_crypto_portfolio(
        self, transaction_data: Dict
    ) -> CryptoTransaction:
        transaction = CryptoTransaction(**transaction_data)
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)

        return transaction

    def update_transaction_in_crypto_portfolio(
        self, transaction: CryptoTransaction, update_data: Dict
    ) -> CryptoTransaction:
        for key, value in update_data.items():
            if value is None:
                continue
            setattr(transaction, key, value)

        self.db.commit()
        self.db.refresh(transaction)

        return transaction

    def delete_transaction_in_crypto_portfolio(
        self, transaction: CryptoTransaction
    ) -> bool:
        self.db.delete(transaction)
        self.db.commit()
        return True

    def delete_all_transactions_in_crypto_portfolio(
        self, portfolio_id: str, crypto: Crypto = None
    ) -> bool:
        transactions = self.db.query(CryptoTransaction).filter(
            CryptoTransaction.portfolio_id == portfolio_id
        )
        if crypto:
            transactions = transactions.filter(CryptoTransaction.crypto == crypto)
        transactions = transactions.all()
        if not transactions:
            return False
        for transaction in transactions:
            self.db.delete(transaction)
        self.db.commit()
        return True
