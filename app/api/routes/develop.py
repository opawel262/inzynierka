from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy import MetaData, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.domain.model_base import Base
from app.core.database import engine
from app.api.deps import get_db
from app.core.utils import limiter
from app.core.security import get_password_hash
from app.core.config import settings
from app.domain.user.models import User
from app.domain.budget.models import Category
from app.domain.budget.utils import categories
from app.domain.portfolio.repositories.stock_repository import StockRepository
from app.domain.portfolio.repositories.crypto_repository import CryptoRepository
from app.domain.portfolio.services.gpw_stock_service import GPWStockService
from app.domain.portfolio.services.coingecko_crypto_service import (
    CoinGeckoCryptoService,
)
from app.domain.portfolio.services.binanace_crypto_service import BinanaceCryptoService
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
    prefix="/develop",
    tags=["Development Utilities"],
)


@router.delete("/clear-database")
@limiter.limit("60/minute")
def clear_data(request: Request, db: Session = Depends(get_db)):
    try:
        metadata = MetaData()
        metadata.reflect(bind=engine)

        with engine.connect() as conn:
            # Disable foreign key checks if necessary (depends on your DBMS)
            # conn.execute("SET FOREIGN_KEY_CHECKS = 0")

            # Delete all rows from tables in reverse order to handle foreign key constraints
            for table in reversed(metadata.sorted_tables):
                conn.execute(table.delete())

            # Commit the transaction
            conn.commit()

            # Enable foreign key checks if you disabled them
            # conn.execute("SET FOREIGN_KEY_CHECKS = 1")

        return {"message": "All data cleared successfully"}

    except SQLAlchemyError as e:
        db.rollback()  # Ensure the session is rolled back on error
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/drop-database-tables")
@limiter.limit("60/minute")
def drop_all_tables(request: Request, db: Session = Depends(get_db)):
    try:
        # Reflect the metadata from the database
        metadata = MetaData()
        metadata.reflect(bind=engine)

        with engine.connect() as conn:
            # Begin a transaction
            with conn.begin():
                # Drop tables in reverse order
                for table in reversed(metadata.sorted_tables):
                    drop_table_sql = f"DROP TABLE IF EXISTS {table.name} CASCADE"
                    conn.execute(text(drop_table_sql))

        return {"message": "All tables dropped successfully"}

    except SQLAlchemyError as e:
        db.rollback()  # Roll back the transaction in case of error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/create-example-data")
def create_example_data(request: Request, db: Session = Depends(get_db)):
    if db.query(User).count() > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Example data already exists. Clear the database first.",
        )
    user1 = User(
        email=settings.EXAMPLE_USER_EMAIL,
        username=settings.EXAMPLE_USER_USERNAME,
        password=get_password_hash(settings.EXAMPLE_USER_PASSWORD),
        is_active=True,
    )
    user2 = User(
        email=settings.EXAMPLE_USER_2_EMAIL,
        username=settings.EXAMPLE_USER_2_USERNAME,
        password=get_password_hash(settings.EXAMPLE_USER_2_PASSWORD),
        is_active=True,
    )
    db.add(user1)
    db.add(user2)

    for category in categories:
        category = Category(
            name=category.get("name"),
            icon=category.get("icon"),
        )
        db.add(category)

    db.commit()

    return {"message": "Example data created successfully"}


@router.post("/fetch-and-save-stock", status_code=status.HTTP_200_OK)
@limiter.limit("60/minute")
def fetch_and_save_stock(request: Request, db: Session = Depends(get_db)):
    stock_repository = StockRepository(db_session=db)
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
