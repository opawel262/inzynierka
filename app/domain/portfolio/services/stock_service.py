from typing import List, Dict, Any
from fastapi import HTTPException, status
from app.domain.portfolio.models import Stock, StockHistoricalPrice
from app.domain.portfolio.repositories.stock_repository import StockRepository

from datetime import datetime, timedelta


class StockService:
    def __init__(self, repository: StockRepository):
        self.repository = repository

    def search_stocks(self, search: str | None) -> List[Stock]:

        if search:
            search = search.lower()

            stocks = self.repository.get_stock_by_name_or_symbol_alike(
                name_or_symbol=search
            )

        else:
            stocks = self.repository.get_all_stocks()

        return stocks if stocks else []

    def get_stock_by_symbol(self, symbol: str) -> Stock:
        stock = self.repository.get_stock_by_symbol(symbol=symbol)

        if not stock:
            raise Exception(f"Stock with symbol '{symbol}' not found.")

        return stock

    def get_stock_historical_by_symbol_period_data_from_last(
        self, symbol: str, period: str
    ) -> List[StockHistoricalPrice]:

        if period == "1d":
            from_date = datetime.now() - timedelta(days=1)
        elif period == "1w":
            from_date = datetime.now() - timedelta(weeks=1)
        elif period == "1m":
            from_date = datetime.now() - timedelta(days=30)
        elif period == "1y":
            from_date = datetime.now() - timedelta(days=365)
        else:
            from_date = datetime.now() - timedelta(days=1)
        print(from_date)
        print(period)
        to_date = datetime.now()

        historical_prices = (
            self.repository.get_stock_historical_prices_by_symbol_period_from_to_date(
                symbol=symbol,
                period=period,
                from_date=from_date,
                to_date=to_date,
            )
        )

        return historical_prices

    def get_stock_historical_by_symbol_data_from_last_max(
        self, symbol: str
    ) -> List[StockHistoricalPrice]:
        historical_prices = (
            self.repository.get_stock_historical_prices_by_symbol_period(
                symbol=symbol,
                period="1w",
            )
        )

        return historical_prices
