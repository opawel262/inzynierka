# gpw_repository.py
from app.domain.portfolio.models import (
    StockPortfolio,
    StockTransaction,
    Stock,
    WatchedStockInPortfolio,
)
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

    def get_all_stock_portfolios(self, user_id: str) -> List[StockPortfolio]:
        return (
            self.db.query(StockPortfolio)
            .filter(StockPortfolio.owner_id == user_id)
            .order_by(StockPortfolio.created_at.desc())
            .all()
        )

    def delete_all_stock_portfolios(self, user_id: str) -> None:
        stock_portfolios = (
            self.db.query(StockPortfolio)
            .filter(StockPortfolio.owner_id == user_id)
            .delete()
        )
        if not stock_portfolios:
            return False
        self.db.commit()
        return True

    def delete_stock_portfolio_by_id(self, portfolio_id: str) -> None:
        self.db.query(StockPortfolio).filter(StockPortfolio.id == portfolio_id).delete()
        self.db.commit()
        return True

    def get_stock_portfolio_by_id(self, portfolio_id: str) -> StockPortfolio | None:

        return (
            self.db.query(StockPortfolio)
            .filter(StockPortfolio.id == portfolio_id)
            .first()
        )

    def update_stock_portfolio(
        self, existing_stock_portfolio: StockPortfolio, update_data: Dict
    ) -> StockPortfolio | None:
        for key, value in update_data.items():
            if value is None:
                continue
            setattr(existing_stock_portfolio, key, value)

        self.db.commit()
        self.db.refresh(existing_stock_portfolio)

        return existing_stock_portfolio

    def create_stock_portfolio_transactions(
        self, stock_portfolio: StockPortfolio, stock_portfolio_data: Dict
    ):
        transaction = StockTransaction(**stock_portfolio_data)
        stock_portfolio.transactions.append(transaction)
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(historical_price)

        return historical_price

    def update_stock_portfolio_transaction(
        self, stock_portfolio_transaction: StockTransaction, update_data: Dict
    ) -> StockTransaction:
        for key, value in update_data.items():
            setattr(stock_portfolio_transaction, key, value)
        self.db.commit()
        self.db.refresh(stock_portfolio_transaction)

        return stock_portfolio_transaction

    def get_watched_stock_in_portfolio_by_id(
        self, portfolio_id: str, stock_id: str
    ) -> WatchedStockInPortfolio | None:
        return (
            self.db.query(WatchedStockInPortfolio)
            .filter(
                WatchedStockInPortfolio.portfolio_id == portfolio_id,
                WatchedStockInPortfolio.stock_id == stock_id,
            )
            .first()
        )

    def get_all_watched_stock_from_portfolio(
        self, portfolio_id: str
    ) -> List[WatchedStockInPortfolio]:
        return (
            self.db.query(WatchedStockInPortfolio)
            .filter(WatchedStockInPortfolio.portfolio_id == portfolio_id)
            .all()
        )

    def add_watched_stock_to_portfolio(
        self, portfolio_id: str, stock: Stock
    ) -> WatchedStockInPortfolio:
        watched_stock = WatchedStockInPortfolio(portfolio_id=portfolio_id, stock=stock)
        self.db.add(watched_stock)
        self.db.commit()
        self.db.refresh(watched_stock)
        return watched_stock

    def delete_watched_stock_from_portfolio(
        self, watched_stock: WatchedStockInPortfolio
    ) -> bool:
        self.db.delete(watched_stock)
        self.db.commit()
        return True

    def delete_all_watched_stocks_in_portfolio(self, portfolio_id: str) -> bool:
        watched_stocks = (
            self.db.query(WatchedStockInPortfolio)
            .filter(
                WatchedStockInPortfolio.portfolio_id == portfolio_id,
            )
            .all()
        )
        if not watched_stocks:
            return False
        for watched_stock in watched_stocks:
            self.db.delete(watched_stock)
        self.db.commit()
        return True

    def get_all_transactions_in_stock_portfolio(
        self,
        portfolio_id: str,
        stock: Stock = None,
    ) -> List[StockTransaction]:
        query = self.db.query(StockTransaction).filter(
            StockTransaction.portfolio_id == portfolio_id
        )
        if stock:
            query = query.filter(StockTransaction.stock == stock)
        return query.order_by(StockTransaction.transaction_date.desc()).all()

    def get_transaction_in_stock_portfolio_by_id(
        self, portfolio_id: str, transaction_id: str
    ) -> StockTransaction | None:
        return (
            self.db.query(StockTransaction)
            .filter(
                StockTransaction.portfolio_id == portfolio_id,
                StockTransaction.id == transaction_id,
            )
            .first()
        )

    def create_transaction_in_stock_portfolio(
        self, transaction_data: Dict
    ) -> StockTransaction:
        transaction = StockTransaction(**transaction_data)
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)

        return transaction

    def update_transaction_in_stock_portfolio(
        self, transaction: StockTransaction, update_data: Dict
    ) -> StockTransaction:
        for key, value in update_data.items():
            if value is None:
                continue
            setattr(transaction, key, value)

        self.db.commit()
        self.db.refresh(transaction)

        return transaction

    def delete_transaction_in_stock_portfolio(
        self, transaction: StockTransaction
    ) -> bool:
        self.db.delete(transaction)
        self.db.commit()
        return True

    def delete_all_transactions_in_stock_portfolio(
        self, portfolio_id: str, stock: Stock = None
    ) -> bool:
        transactions = self.db.query(StockTransaction).filter(
            StockTransaction.portfolio_id == portfolio_id
        )
        if stock:
            transactions = transactions.filter(StockTransaction.stock == stock)
        transactions = transactions.all()
        if not transactions:
            return False
        for transaction in transactions:
            self.db.delete(transaction)
        self.db.commit()
        return True
