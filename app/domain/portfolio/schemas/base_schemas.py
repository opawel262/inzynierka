from pydantic import BaseModel
from typing import Optional, Union
from datetime import datetime


class AssetSymbolSchema(BaseModel):
    symbol: str


class AssetSearchSchema(AssetSymbolSchema, BaseModel):
    price: float
    price_change_percentage_1h: Optional[float] = None
    price_change_percentage_24h: Optional[float] = None
    price_change_percentage_7d: Optional[float] = None
    circulating_supply: Optional[float] = None
    currency: str
    volume_24h: Optional[float] = None
    market_cap: Optional[float] = None
    market_cap_rank: Optional[int] = None
    name: str


class AssetPricePerformanceSchema(AssetSymbolSchema):
    price_change_percentage_1h: Optional[float] = None
    price_change_percentage_24h: Optional[float] = None
    price_change_percentage_7d: Optional[float] = None
    price_change_percentage_30d: Optional[float] = None
    price_change_percentage_1y: Optional[float] = None
    price_change_percentage_max: Optional[float] = None
    price: float
    updated_at: Optional[datetime] = None


class AssetLoserGainerSchema(AssetSymbolSchema):
    price_change_percentage_24h: Optional[float] = None
    name: str
    currency: str
    price: float
    price_change_percentage_24h: float


class AssetHistoricalPriceSchema(BaseModel):
    date: datetime
    open_price: Optional[float] = None
    close_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    volume: Optional[Union[int, float]] = None
    interval: str
    period: str
