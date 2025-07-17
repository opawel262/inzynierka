from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional, List


class FetcherHistoricalRecordSchema(BaseModel):
    date: datetime
    open_price: Optional[float] = None
    close_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    volume: Optional[int] = None
    interval: str
    period: str


class FetcherHistoricalStockSchema(BaseModel):
    one_h: Optional[List[FetcherHistoricalRecordSchema]] = Field(None, alias="1h")
    one_d: Optional[List[FetcherHistoricalRecordSchema]] = Field(None, alias="1d")
    one_mo: Optional[List[FetcherHistoricalRecordSchema]] = Field(None, alias="1mo")
    one_y: Optional[List[FetcherHistoricalRecordSchema]] = Field(None, alias="1y")
    max_: Optional[List[FetcherHistoricalRecordSchema]] = Field(None, alias="max")

    class Config:
        populate_by_name = True


class FetcherStockGPWSchema(BaseModel):
    symbol: Optional[str] = None
    name: Optional[str] = None
    sector: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    volume_24h: Optional[float] = None
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
    price_change_percentage_1h: Optional[float] = None
    price_change_percentage_24h: Optional[float] = None
    price_change_percentage_7d: Optional[float] = None
    circulating_supply: Optional[float] = None

    @field_validator("*", mode="before")
    @classmethod
    def unwrap_single_element_tuple(cls, v):
        if isinstance(v, tuple) and len(v) == 1:
            return v[0]
        return v


class FetcherCoinGeckoCryptoSchema(BaseModel):
    symbol: Optional[str] = None
    name: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    market_cap: Optional[float] = None
    price_change_percentage_1h: Optional[float] = None
    price_change_percentage_24h: Optional[float] = None
    price_change_percentage_7d: Optional[float] = None
    volume_24h: Optional[float] = None
    circulating_supply: Optional[float] = None
    icon: Optional[str] = None
    market_cap_rank: Optional[int] = None
    total_supply: Optional[float] = None
    max_supply: Optional[float] = None
