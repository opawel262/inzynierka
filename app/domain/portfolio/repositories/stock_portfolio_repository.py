# stock_portfolio_repository.py
from app.domain.portfolio.models import StockPortfolio, StockTransaction
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime


class StockPortfolioRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_stock_portfolio(self, stock_portfolio_data: Dict) -> StockPortfolio:
        stock_portfolio = StockPortfolio(**stock_portfolio_data)
        self.db.add(stock_portfolio)
        self.db.commit()
        self.db.refresh(stock_portfolio)
        return stock_portfolio

    def get_all_stock_portfolios(self) -> List[StockPortfolio]:
        return (
            self.db.query(StockPortfolio)
            .order_by(StockPortfolio.created_at.desc())
            .all()
        )

    def get_stock_portfolio_by_id(self, portfolio_id: int) -> StockPortfolio | None:
        return (
            self.db.query(StockPortfolio)
            .filter(StockPortfolio.id == portfolio_id)
            .first()
        )

    def update_stock_portfolio(self, update_data: Dict) -> StockPortfolio | None:
        existing_stock_portfolio = self.get_stock_portfolio_by_id(update_data["id"])
        if not existing_stock_portfolio:
            raise ValueError(
                f"Stock portfolio with id {update_data['id']} does not exist."
            )
        for key, value in update_data.items():
            setattr(existing_stock_portfolio, key, value)
        self.db.commit()
        self.db.refresh(existing_stock_portfolio)
        return existing_stock_portfolio

    def create_stock_portfolio_transaction(
        self, stock_portfolio: StockPortfolio, stock_transaction_data: Dict
    ) -> StockTransaction:
        transaction = StockTransaction(**stock_transaction_data)
        stock_portfolio.transactions.append(transaction)
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def update_stock_portfolio_transaction(
        self, stock_portfolio_transaction: StockTransaction, update_data: Dict
    ) -> StockTransaction:
        for key, value in update_data.items():
            setattr(stock_portfolio_transaction, key, value)
        self.db.commit()
        self.db.refresh(stock_portfolio_transaction)
        return stock_portfolio_transaction
