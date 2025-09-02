from pydantic import BaseModel
from app.domain.portfolio.schemas.base_schemas import (
    AssetSymbolSchema,
    AssetSearchSchema,
    AssetPricePerformanceSchema,
    AssetLoserGainerSchema,
)
from datetime import datetime
from typing import Optional


class CryptoSymbolSchema(AssetSymbolSchema):
    pass


class CryptoBasicSchema(CryptoSymbolSchema):
    name: str
    currency: str
    volume_24h: Optional[float] = None
    market_cap: Optional[float] = None
    circulating_supply: Optional[float] = None
    market_cap_rank: Optional[int] = None
    icon: Optional[str] = None
    circulating_supply: Optional[float] = None
    updated_at: Optional[datetime] = None


class CryptoSearchSchema(AssetSearchSchema):
    icon: Optional[str] = None


class CryptoPricePerformanceSchema(AssetPricePerformanceSchema):
    pass


class CryptoLoserGainerSchema(AssetLoserGainerSchema):
    icon: Optional[str] = None


class CryptoBiggestMarketSchema(CryptoPricePerformanceSchema, CryptoLoserGainerSchema):
    pass


class CryptoFetcherSchema(CryptoBasicSchema, CryptoSearchSchema):
    pass
