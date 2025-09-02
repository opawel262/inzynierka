from fastapi import APIRouter, HTTPException, status, Depends, Request
from typing import Annotated
from sqlalchemy.orm import Session
from app.api.deps import get_db, authenticate
from app.core.utils import limiter
from app.domain.portfolio.services.crypto_portfolio_service import (
    CryptoPortfolioService,
)
from app.domain.portfolio.repositories.crypto_portfolio_repository import (
    CryptoPortfolioRepository,
)
from fastapi_pagination import Page, paginate
from app.domain.portfolio.schemas.crypto_portfolio_schemas import (
    CryptoPortfolioCreateSchema,
    CryptoPortfolioSchema,
)

router = APIRouter(
    prefix="/portfolios/cryptos",
    tags=["Portfolio Management - Cryptos"],
)


@router.get(
    "",
)
@limiter.limit("5/second")
def get_portfolio_cryptos(
    request: Request,
    user_id: Annotated[str, Depends(authenticate)],
    db: Session = Depends(get_db),
) -> Page[CryptoPortfolioSchema]:
    crypto_portfolio_repository = CryptoPortfolioRepository(db)
    crypto_portfolio_service = CryptoPortfolioService(
        crypto_portfolio_repository, user_id
    )
    crypto_portfolios = crypto_portfolio_service.get_all_portfolios()
    return paginate(crypto_portfolios)


@router.post("")
@limiter.limit("1/second")
def create_portfolio_crypto(
    request: Request,
    create_data: CryptoPortfolioCreateSchema,
    user_id: Annotated[str, Depends(authenticate)],
    db: Session = Depends(get_db),
) -> CryptoPortfolioSchema:
    crypto_portfolio_repository = CryptoPortfolioRepository(db)
    crypto_portfolio_service = CryptoPortfolioService(
        crypto_portfolio_repository, user_id
    )
    crypto_portfolio = crypto_portfolio_service.create_portfolio(
        create_data.model_dump()
    )
    return crypto_portfolio


@router.delete("")
@limiter.limit("1/second")
def delete_all_portfolio_cryptos(
    request: Request, db: Session = Depends(get_db), user_id=Depends(authenticate)
):
    crypto_portfolio_repository = CryptoPortfolioRepository(db)
    crypto_portfolio_service = CryptoPortfolioService(
        crypto_portfolio_repository, user_id
    )
    return crypto_portfolio_service.delete_all_portfolios()


@router.get("/{portfolio_id}", deprecated=True)
def get_detail_portfolio_crypto(portfolio_id: int, db: Session = Depends(get_db)):
    pass


@router.patch("/{portfolio_id}", deprecated=True)
def update_portfolio_crypto(portfolio_id: int, db: Session = Depends(get_db)):
    pass


@router.delete("/{portfolio_id}", deprecated=True)
def delete_portfolio_crypto(portfolio_id: int, db: Session = Depends(get_db)):
    pass


@router.post("/{portfolio_id}/watched_cryptos/{symbol}", deprecated=True)
def add_watched_crypto(portfolio_id: int, symbol: str, db: Session = Depends(get_db)):
    pass


@router.delete("/{portfolio_id}/watched_cryptos/{symbol}", deprecated=True)
def remove_watched_crypto(
    portfolio_id: int, symbol: str, db: Session = Depends(get_db)
):
    pass


@router.delete("/{portfolio_id}/watched_cryptos", deprecated=True)
def remove_all_watched_cryptos(portfolio_id: int, db: Session = Depends(get_db)):
    pass


@router.get("/{portfolio_id}/transactions", deprecated=True)
def get_portfolio_crypto_transactions(portfolio_id: int, db: Session = Depends(get_db)):
    pass


@router.post("/{portfolio_id}/transactions", deprecated=True)
def create_portfolio_crypto_transaction(
    portfolio_id: int, db: Session = Depends(get_db)
):
    pass


@router.get("/{portfolio_id}/transactions/{transaction_id}", deprecated=True)
def get_detail_portfolio_crypto_transaction(
    portfolio_id: int, transaction_id: int, db: Session = Depends(get_db)
):
    pass


@router.patch("/{portfolio_id}/transactions/{transaction_id}", deprecated=True)
def update_portfolio_crypto_transaction(
    portfolio_id: int, transaction_id: int, db: Session = Depends(get_db)
):
    pass


@router.delete("/{portfolio_id}/transactions/{transaction_id}", deprecated=True)
def delete_portfolio_crypto_transaction(
    portfolio_id: int, transaction_id: int, db: Session = Depends(get_db)
):
    pass
