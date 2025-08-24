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

        return stock

    def get_stock_historical_by_symbol_period_data_from_last(
        self, symbol: str, period: str
    ) -> List[StockHistoricalPrice]:

        if (
            period == "1d"
        ):  # There is no option in endpoint for this but it can be changed it later
            from_date = datetime.now() - timedelta(days=1)
        elif period == "1w":
            from_date = datetime.now() - timedelta(weeks=1)
        elif period == "1m":
            from_date = datetime.now() - timedelta(days=30)
        elif period == "1y":
            from_date = datetime.now() - timedelta(days=365)
        else:
            from_date = datetime.now() - timedelta(days=1)
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
                period="max",
            )
        )

        return historical_prices

    def get_global_performance_data(self) -> Dict[str, Any]:
        stocks = self.repository.get_all_stocks()

        total_volume_24h = sum(float(c.volume_24h) or 0 for c in stocks)
        total_market_cap = round(sum(float(c.market_cap) or 0 for c in stocks), 0)
        top_gainers_24h = self.repository.get_stocks_biggest_gainers()
        top_losers_24h = self.repository.get_stocks_biggest_losers()
        top_biggest_market_cap = self.repository.get_stocks_biggest_market_cap()

        return {
            "total_volume_24h": total_volume_24h,
            "total_market_cap": total_market_cap,
            "top_gainers_24h": top_gainers_24h,
            "top_losers_24h": top_losers_24h,
            "top_market_cap_rank": top_biggest_market_cap,
        }
