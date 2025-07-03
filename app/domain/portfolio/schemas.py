from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class FetcherHistoricalRecordSchema(BaseModel):
    date: datetime
    open_price: Optional[float] = None
    close_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    volume: Optional[float] = None
    interval: str
    period: str


class FetcherHistoricalStockSchema(BaseModel):
    one_h: Optional[FetcherHistoricalRecordSchema] = Field(None, alias="1h")
    one_d: Optional[FetcherHistoricalRecordSchema] = Field(None, alias="1d")
    seven_d: Optional[FetcherHistoricalRecordSchema] = Field(None, alias="7d")
    one_mo: Optional[FetcherHistoricalRecordSchema] = Field(None, alias="1mo")
    one_y: Optional[FetcherHistoricalRecordSchema] = Field(None, alias="1y")
    max_: Optional[FetcherHistoricalRecordSchema] = Field(None, alias="max")

    class Config:
        populate_by_name = True


class FetcherStockGPWSchema(BaseModel):
    symbol: Optional[str] = None
    name: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    sector: Optional[str] = None
    current_price: Optional[float] = None
    volume: Optional[int] = None
    market_cap: Optional[float] = None
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
    price_1h_ago: Optional[float] = None
    price_24h_ago: Optional[float] = None
    price_7d_ago: Optional[float] = None
    change_1h: Optional[float] = None
    change_24h: Optional[float] = None
    change_7d: Optional[float] = None
    historical_data: Optional[FetcherHistoricalStockSchema] = None
