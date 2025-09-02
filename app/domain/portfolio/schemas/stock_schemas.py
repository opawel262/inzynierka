from pydantic import BaseModel
from app.domain.portfolio.schemas.base_schemas import (
    AssetSymbolSchema,
    AssetSearchSchema,
    AssetPricePerformanceSchema,
    AssetLoserGainerSchema,
)
from typing import Optional
from datetime import datetime


class StockSymbolSchema(AssetSymbolSchema):
    pass


class StockBasicSchema(StockSymbolSchema):
    name: Optional[str] = None
    sector: Optional[str] = None
    currency: Optional[str] = None
    volume_24h: Optional[float] = None
    market_cap: Optional[float] = None
    market_cap_rank: Optional[float] = None
    market_state: Optional[str] = None
    description: Optional[str] = None
    debt_to_equity: Optional[float] = None
    trailing_annual_dividend_yield: Optional[float] = None
    return_on_equity: Optional[float] = None
    free_cashflow: Optional[float] = None
    payout_ratio: Optional[float] = None
    price_to_book: Optional[float] = None
    price_to_sales: Optional[float] = None
    eps_trailing_twelve_months: Optional[float] = None
    beta: Optional[float] = None
    pe_ratio: Optional[float] = None
    average_volume_10d: Optional[float] = None
    employees: Optional[int] = None
    circulating_supply: Optional[float] = None
    updated_at: Optional[datetime] = None


class StockSearchSchema(AssetSearchSchema):
    market_state: Optional[str] = None


class StockPricePerformanceSchema(StockSymbolSchema, AssetPricePerformanceSchema):
    pass


class StockLoserGainerSchema(AssetLoserGainerSchema):
    pass


class StockBiggestMarketSchema(StockPricePerformanceSchema, StockLoserGainerSchema):
    pass


class StockFetcherSchema(StockBasicSchema, StockPricePerformanceSchema):
    pass
