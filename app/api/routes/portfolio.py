from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.core.utils import limiter
from app.core.config import settings
from app.domain.portfolio.repositories.gpw_stock_repository import GPWStockRepository
from app.domain.portfolio.services.gpw_stock_service import GPWStockService
from app.domain.portfolio.fetchers.stock_gpw_fetcher import GPWStockFetcher

router = APIRouter(
    prefix="/portfolio",
    tags=["Portfolio Management"],
)


@router.post("/fetch-and-save-stock", status_code=status.HTTP_200_OK)
@limiter.limit("60/minute")
def fetch_and_save_stock(request: Request, db: Session = Depends(get_db)):
    stock_repository = GPWStockRepository(db_session=db)
    stock_service = GPWStockService(
        fetcher=GPWStockFetcher(), repository=stock_repository
    )
    gpw_fetcher = GPWStockFetcher()
    for ticker in gpw_fetcher.tickers:
        stock_data = gpw_fetcher.fetch_stock_data_by_ticker(ticker)
        if not stock_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stock data for ticker {ticker} not found",
            )
    stock_service.fetch_and_save_stock_data()
    return {"message": "Stock data fetched and saved successfully"}
