from typing import List, Dict, Any
from fastapi import HTTPException, status
from app.domain.portfolio.repositories.gpw_stock_repository import GPWStockRepository
from app.domain.portfolio.models import Stock, StockHistoricalPrice
from app.domain.portfolio.fetchers.stock_gpw_fetcher import GPWStockFetcher
from app.domain.portfolio.schemas import FetcherStockGPWSchema


class GPWStockService:
    def __init__(self, fetcher: GPWStockFetcher, repository: GPWStockRepository):
        self.fetcher = fetcher
        self.repository = repository

    def fetch_and_save_stock_data(self):
        for ticker in self.fetcher.tickers:
            stock_data = self.fetcher.fetch_stock_data_by_ticker(ticker)

            if not stock_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Stock data for ticker {ticker} not found",
                )
            stock = self.repository.get_stock_by_symbol(ticker)

            validated_stock_data = FetcherStockGPWSchema(**stock_data).model_dump()

            if stock:
                self.repository.update_stock(validated_stock_data)
            else:
                stock = self.repository.create_stock(validated_stock_data)

            historical_data = self.fetcher.historical_data_from_last_fetch()

            for data in historical_data:
                historical_stock_price = (
                    self.repository.get_stock_historical_price_by_symbol_period_date(
                        symbol=stock.symbol, period=data["period"], date=data["date"]
                    )
                )
                if historical_stock_price:
                    print("POTWARZA SIE OIMG ALE KOX")
                    continue
                else:
                    self.repository.create_stock_historical_price(stock, data)
