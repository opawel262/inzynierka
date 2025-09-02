# from typing import List, Optional, Literal, Dict

# from fastapi import APIRouter, HTTPException, status, Depends, Request, Query
# from sqlalchemy.orm import Session
# from fastapi_pagination import Page, paginate

# from app.api.deps import get_db
# from app.core.utils import limiter
# from app.core.config import settings
# from app.domain.portfolio.repositories.stock_repository import StockRepository
# from app.domain.portfolio.services.stock_service import StockService
# from app.domain.portfolio.services.crypto_service import CryptoService
# from app.domain.portfolio.repositories.crypto_repository import CryptoRepository
# from app.domain.portfolio.repositories.currency_repository import (
#     CurrencyPairRateRepository,
# )
# from app.domain.portfolio.services.currency_service import (
#     CurrencyService,
# )
# from app.domain.portfolio.schemas import (
#     FetcherStockGPWSchema,
#     FetcherHistoricalStockRecordSchema,
#     BasicStockSchema,
#     BasicCryptoSchema,
#     GeneralStockGPWSchema,
#     PricePerformanceStockGPWSchema,
#     PricePerformanceCryptochema,
#     SymbolStockSchema,
#     SymbolCryptoSchema,
#     GlobalMarketPerformanceSchema,
#     CurrencyPairRateSchema,
#     CryptoSearchSchema,
# )
# from fastapi.responses import JSONResponse
# from fastapi.encoders import jsonable_encoder

# router = APIRouter(
#     prefix="/portfolio/stocks/",
#     tags=["Stock Portfolio"],
# )


# @router.get("/stocks", status_code=status.HTTP_200_OK)
# @limiter.limit("1/second")
# def get_s
