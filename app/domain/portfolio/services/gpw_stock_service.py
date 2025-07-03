from typing import List, Dict, Any
from fastapi import HTTPException, status
from app.domain.portfolio.repositories.gpw_stock_repository import GPWStockRepository
from app.domain.portfolio.models import Stock
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

            stock = Stock(**stock_data)

            self.repository.create_stock(stock)
