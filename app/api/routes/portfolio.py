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
from app.domain.portfolio.fetchers.currency_exchange_fetcher import (
    ExchangerateCurrencyRateFetcher,
)
from app.domain.portfolio.repositories.currency_exchange_repository import (
    CurrencyPairRateRepository,
)
from app.domain.portfolio.services.currency_exchange_service import (
    ExchangeRateCurrencyService,
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

    crypto_historical_service = BinanaceCryptoService(
        fetcher=BinanaceCryptoFetcher(), repository=CryptoRepository(db_session=db)
    )

    crypto_historical_data = (
        crypto_historical_service.fetch_and_save_historical_cryptos_data()
    )

    return {"message": "Crypto data fetched successfully", "data": crypto_data}


@router.post("/fetch-binanace-crypto", status_code=status.HTTP_200_OK)
@limiter.limit("60/minute")
def fetch_binanace_crypto_data(request: Request, db: Session = Depends(get_db)):
    binanace_crypto_service = BinanaceCryptoService(
        fetcher=BinanaceCryptoFetcher(), repository=CryptoRepository(db_session=db)
    )

    binanace_crypto_service.fetch_and_save_historical_crypto_data()

    return {"message": "Binance crypto data fetched successfully"}


@router.post("/fetch-currency-exchange-rates", status_code=status.HTTP_200_OK)
@limiter.limit("60/minute")
def fetch_currency_exchange_rates(request: Request, db: Session = Depends(get_db)):

    currency_exchange_service = ExchangeRateCurrencyService(
        fetcher=ExchangerateCurrencyRateFetcher(),
        repository=CurrencyPairRateRepository(db_session=db),
    )

    currency_exchange_service.fetch_and_save_currency_pair_rate()

    return {"message": "Currency exchange rates fetched and saved successfully"}
