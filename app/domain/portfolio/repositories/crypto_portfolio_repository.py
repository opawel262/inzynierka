# gpw_repository.py
from app.domain.portfolio.models import CryptoPortfolio, CryptoTransaction
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
        self.db.query(CryptoPortfolio).filter(
            CryptoPortfolio.owner_id == user_id
        ).delete()
        self.db.commit()
        return True

    def get_crypto_portfolio_by_id(self, portfolio_id: int) -> CryptoPortfolio | None:

        return (
            self.db.query(CryptoPortfolio)
            .filter(CryptoPortfolio.id == portfolio_id)
            .first()
        )

    def update_crypto_portfolio(self, update_data: Dict) -> CryptoPortfolio | None:
        existing_crypto_portfolio = self.get_crypto_portfolio_by_id(update_data["id"])
        if not existing_crypto_portfolio:
            raise ValueError(
                f"Crypto portfolio with id {update_data['id']} does not exist."
            )
        for key, value in update_data.items():
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
