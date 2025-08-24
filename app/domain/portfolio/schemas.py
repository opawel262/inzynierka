from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional, List, Dict, Any, Union


## STOCKS
class SymbolStockSchema(BaseModel):
    symbol: str


class SymbolCryptoSchema(SymbolStockSchema):
    pass


class BasicStockSchema(SymbolStockSchema):
    name: str
    price: float
    currency: str
    volume_24h: Optional[float] = None
    market_cap: Optional[float] = None
    market_state: Optional[str] = None
    price_change_percentage_1h: Optional[float] = None
    price_change_percentage_24h: Optional[float] = None
    price_change_percentage_7d: Optional[float] = None
    circulating_supply: Optional[float] = None
    market_cap_rank: Optional[int] = None


class FetcherHistoricalStockRecordSchema(BaseModel):
    date: datetime
    open_price: Optional[float] = None
    close_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    volume: Optional[Union[int, float]] = None
    interval: str
    period: str


class FetcherHistoricalCryptoRecordSchema(FetcherHistoricalStockRecordSchema):
    volume: Optional[float] = None


class FetcherHistoricalStockSchema(BaseModel):
    one_h: Optional[List[FetcherHistoricalStockRecordSchema]] = Field(None, alias="1h")
    one_d: Optional[List[FetcherHistoricalStockRecordSchema]] = Field(None, alias="1d")
    one_mo: Optional[List[FetcherHistoricalStockRecordSchema]] = Field(
        None, alias="1mo"
    )
    one_y: Optional[List[FetcherHistoricalStockRecordSchema]] = Field(None, alias="1y")
    max_: Optional[List[FetcherHistoricalStockRecordSchema]] = Field(None, alias="max")

    class Config:
        populate_by_name = True


class GeneralStockGPWSchema(BaseModel):
    symbol: Optional[str] = None
    name: Optional[str] = None
    sector: Optional[str] = None
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
    circulating_supply: Optional[float] = None
    updated_at: Optional[datetime] = None


class PricePerformanceCryptochema(BaseModel):
    price: float
    price_change_percentage_1h: Optional[float] = None
    price_change_percentage_24h: Optional[float] = None
    price_change_percentage_7d: Optional[float] = None
    price_change_percentage_30d: Optional[float] = None
    price_change_percentage_1y: Optional[float] = None
    price_change_percentage_max: Optional[float] = None
    updated_at: Optional[datetime] = None


class PricePerformanceStockGPWSchema(PricePerformanceCryptochema):
    pass


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
    price_change_percentage_30d: Optional[float] = None
    price_change_percentage_1y: Optional[float] = None
    price_change_percentage_max: Optional[float] = None
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


## CRYPTOS


class BasicCryptoSchema(BaseModel):
    symbol: str
    name: str
    currency: str
    volume_24h: Optional[float] = None
    market_cap: Optional[float] = None
    circulating_supply: Optional[float] = None
    market_cap_rank: Optional[int] = None
    icon: Optional[str] = None
    circulating_supply: Optional[float] = None
    updated_at: Optional[datetime] = None


## GLOBAL
class CryptoGainersLosersSchema(BaseModel):
    symbol: str
    name: str
    currency: str
    icon: Optional[str] = None
    price: float
    price_change_percentage_24h: float


class CryptoBiggestMarketSchema(CryptoGainersLosersSchema):
    price_change_percentage_7d: float
    price_change_percentage_30d: float
    price_change_percentage_1y: float
    price_change_percentage_max: float


class GlobalCryptoPerformanceSchema(BaseModel):
    total_volume_24h: float
    total_market_cap: float
    top_gainers_24h: List[CryptoGainersLosersSchema]
    top_losers_24h: List[CryptoGainersLosersSchema]

    top_market_cap_rank: List[CryptoBiggestMarketSchema]


class StockoGainersLosersSchema(BaseModel):
    symbol: str
    name: str
    currency: str
    price: float
    price_change_percentage_24h: float


class StockBiggestMarketSchema(StockoGainersLosersSchema):
    price_change_percentage_7d: float
    price_change_percentage_30d: float
    price_change_percentage_1y: float
    price_change_percentage_max: float


class GlobalStockPerformanceSchema(BaseModel):
    total_volume_24h: float
    total_market_cap: float
    top_gainers_24h: List[StockoGainersLosersSchema]
    top_losers_24h: List[StockoGainersLosersSchema]

    top_market_cap_rank: List[StockBiggestMarketSchema]


class GlobalCryptoPerformanceSchema(GlobalCryptoPerformanceSchema):
    pass


class GlobalMarketPerformanceSchema(BaseModel):
    global_crypto_data: GlobalCryptoPerformanceSchema
    global_stock_data: GlobalStockPerformanceSchema


# PAIR RATE


class CurrencyPairRateSchema(BaseModel):
    id: int
    base_currency: str
    quote_currency: str
    rate: float
    updated_at: datetime
