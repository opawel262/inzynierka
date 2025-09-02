from pydantic import BaseModel
from app.domain.portfolio.schemas.crypto_schemas import (
    CryptoLoserGainerSchema,
    CryptoBiggestMarketSchema,
)

from app.domain.portfolio.schemas.stock_schemas import (
    StockLoserGainerSchema,
    StockBiggestMarketSchema,
)
from typing import List


class GlobalCryptoPerformanceSchema(BaseModel):
    total_volume_24h: float
    total_market_cap: float
    top_gainers_24h: List[CryptoLoserGainerSchema]
    top_losers_24h: List[CryptoLoserGainerSchema]

    top_market_cap_rank: List[CryptoBiggestMarketSchema]


class GlobalStockPerformanceSchema(BaseModel):
    total_volume_24h: float
    total_market_cap: float
    top_gainers_24h: List[StockLoserGainerSchema]
    top_losers_24h: List[StockLoserGainerSchema]

    top_market_cap_rank: List[StockBiggestMarketSchema]


class GlobalMarketPerformanceSchema(BaseModel):
    global_crypto_data: GlobalCryptoPerformanceSchema
    global_stock_data: GlobalStockPerformanceSchema
