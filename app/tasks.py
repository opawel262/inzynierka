from typing import List
from sqlalchemy.orm import Session
from app.core.database import SessionLocal

from app.domain.portfolio.repositories.gpw_stock_repository import GPWStockRepository
from app.domain.portfolio.services.gpw_stock_service import GPWStockService
from app.domain.portfolio.fetchers.stock_gpw_fetcher import GPWStockFetcher
from app.domain.portfolio.fetchers.crypto_fetchers import (
    CoinGeckoCryptoFetcher,
    BinanaceCryptoFetcher,
)
from app.domain.portfolio.services.crypto_services import (
    CoinGeckoCryptoService,
    BinanaceCryptoService,
)
from app.domain.portfolio.repositories.crypto_repository import CryptoRepository
from app.domain.portfolio.fetchers.currency_exchange_fetcher import (
    ExchangerateCurrencyRateFetcher,
)
from app.domain.portfolio.repositories.currency_exchange_repository import (
    CurrencyPairRateRepository,
)
from app.domain.portfolio.services.currency_exchange_service import (
    ExchangeRateCurrencyService,
)

from app.celery_app import celery_app


@celery_app.task(name="app.tasks.fetch_gpw_data_by_tickers")
def fetch_gpw_data_by_tickers(tickers: List[str]) -> None:
    db: Session = SessionLocal()
    try:
        stock_service = GPWStockService(
            fetcher=GPWStockFetcher(tickers=tickers),
            repository=GPWStockRepository(db_session=db),
        )
        stock_service.fetch_and_save_stock_data()
    finally:
        db.close()


@celery_app.task(name="app.tasks.fetch_coingecko_data")
def fetch_coingecko_data() -> None:
    db: Session = SessionLocal()
    try:
        stock_service = CoinGeckoCryptoService(
            fetcher=CoinGeckoCryptoFetcher(), repository=CryptoRepository(db_session=db)
        )
        stock_service.fetch_and_save_crypto_data()
    finally:
        db.close()


@celery_app.task(name="app.tasks.fetch_binanace_data")
def fetch_binanace_data() -> None:
    db: Session = SessionLocal()
    try:
        binanace_crypto_service = BinanaceCryptoService(
            fetcher=BinanaceCryptoFetcher(), repository=CryptoRepository(db_session=db)
        )
        binanace_crypto_service.fetch_and_save_historical_crypto_data()
    finally:
        db.close()


@celery_app.task(name="app.tasks.fetch_currency_exchange_rates")
def fetch_currency_exchange_rates() -> None:
    db: Session = SessionLocal()
    try:

        currency_service = ExchangeRateCurrencyService(
            fetcher=ExchangerateCurrencyRateFetcher(),
            repository=CurrencyPairRateRepository(db_session=db),
        )
        currency_service.fetch_and_save_currency_rates()
    finally:
        db.close()
