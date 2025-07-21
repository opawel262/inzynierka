from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.core.utils import limiter
from app.core.config import settings
from app.domain.portfolio.repositories.gpw_stock_repository import GPWStockRepository
from app.domain.portfolio.repositories.crypto_repository import CryptoRepository
from app.domain.portfolio.services.gpw_stock_service import GPWStockService
from app.domain.portfolio.services.crypto_services import (
    CoinGeckoCryptoService,
    BinanaceCryptoService,
)
from app.domain.portfolio.fetchers.stock_gpw_fetcher import GPWStockFetcher
from app.domain.portfolio.fetchers.crypto_fetchers import (
    CoinGeckoCryptoFetcher,
    BinanaceCryptoFetcher,
)

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
    gpw_fetcher = GPWStockFetcher(tickers=settings.GPW_TICKERS)

    stock_service.fetch_and_save_stock_data()
    return {"message": "Stock data fetched and saved successfully"}


@router.post("/fetch-crypto", status_code=status.HTTP_200_OK)
@limiter.limit("60/minute")
def fetch_crypto_data(request: Request, db: Session = Depends(get_db)):
    crypto_service = CoinGeckoCryptoService(
        fetcher=CoinGeckoCryptoFetcher(), repository=CryptoRepository(db_session=db)
    )

    # Fetch crypto data from CoinGecko
    crypto_data = crypto_service.fetch_and_save_crypto_data()
    print(f"[INFO] Fetched {len(crypto_data)} crypto items")

    crypto_historical_service = BinanaceCryptoService(
        fetcher=BinanaceCryptoFetcher(), repository=CryptoRepository(db_session=db)
    )

    crypto_historical_data = (
        crypto_historical_service.fetch_and_save_historical_cryptos_data()
    )

    print(crypto_historical_data)
    return {"message": "Crypto data fetched successfully", "data": crypto_data}
