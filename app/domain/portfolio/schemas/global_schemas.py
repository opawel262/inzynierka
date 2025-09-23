from pydantic import BaseModel
from app.domain.portfolio.schemas.crypto_schemas import (
    CryptoLoserGainerSchema,
    CryptoBiggestMarketSchema,
    CryptoSearchSchema,
)

from app.domain.portfolio.schemas.stock_schemas import (
    StockLoserGainerSchema,
    StockBiggestMarketSchema,
    StockSearchSchema,
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


class GlobalSearchResultsSchema(BaseModel):
    stocks: List[StockSearchSchema]
    cryptos: List[CryptoSearchSchema]


class StockConvertList(BaseModel):
    symbol: str
    name: str


class CryptoConvertList(StockConvertList):
    icon: str


class CurrencyConvertList(StockConvertList):
    pass


class GlobalAssetsToConvert(BaseModel):
    stocks: List[StockConvertList]
    cryptos: List[CryptoConvertList]
    currencies: List[CurrencyConvertList]
