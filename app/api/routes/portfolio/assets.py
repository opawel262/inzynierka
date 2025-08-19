from typing import List, Optional, Literal

from fastapi import APIRouter, HTTPException, status, Depends, Request, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.utils import limiter
from app.core.config import settings
from app.domain.portfolio.repositories.stock_repository import StockRepository
from app.domain.portfolio.services.stock_service import StockService
from app.domain.portfolio.schemas import FetcherStockGPWSchema, BasicStockSchema
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

router = APIRouter(
    prefix="/portfolio/assets",
    tags=["Assets Data"],
)


@router.get("/stocks", status_code=status.HTTP_200_OK)
@limiter.limit("1/second")
def get_stocks_data(
    request: Request,
    search: Optional[str] = Query(
        None, description="Search term for stock names by ticker or name"
    ),
    db: Session = Depends(get_db),
) -> List[BasicStockSchema]:
    """
    Return stock data from GPW.
    """
    stock_repository = StockRepository(db_session=db)
    stock_service = StockService(repository=stock_repository)

    stocks_data = stock_service.search_stocks(search=search)

    return stocks_data


@router.get("/stocks/{symbol}", status_code=status.HTTP_200_OK)
def get_stock_details(
    symbol: str, db: Session = Depends(get_db)
) -> FetcherStockGPWSchema:
    """
    Return detailed information about a specific stock by its symbol.
    """
    stock_repository = StockRepository(db_session=db)
    stock_service = StockService(repository=stock_repository)
    stock = stock_service.get_stock_by_symbol(symbol=symbol)
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Spółka z symbolem '{symbol}' nie została znaleziona.",
        )

    return stock


@router.get("/stocks/{symbol}/historical", status_code=status.HTTP_200_OK)
def get_stock_historical_data(
    symbol: str,
    period: Literal["1d", "1w", "1m", "1y", "max"] = Query(
        "1d",
        description="Period for historical data.",
    ),
    db: Session = Depends(get_db),
):
    if not symbol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Symbol jest wymagany.",
        )

    if period not in ["1d", "1w", "1m", "1y", "max"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nieprawidłowy okres. Dostępne okresy to: 1d, 1w, 1m, 1y, max.",
        )

    stock_repository = StockRepository(db_session=db)
    stock_service = StockService(repository=stock_repository)
    if period == "max":
        historical_data = (
            stock_service.get_stock_historical_by_symbol_data_from_last_max(
                symbol=symbol
            )
        )
    else:
        historical_data = (
            stock_service.get_stock_historical_by_symbol_period_data_from_last(
                symbol=symbol, period=period
            )
        )

    if not historical_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brak danych historycznych dla spółki z symbolem '{symbol}' w okresie '{period}'.",
        )
    return historical_data
