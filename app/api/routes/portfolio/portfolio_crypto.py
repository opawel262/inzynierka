from fastapi import APIRouter, HTTPException, status, Depends, Request
from typing import Annotated
from sqlalchemy.orm import Session
from app.api.deps import get_db, authenticate
from app.core.utils import limiter
from app.core.exceptions import UnauthorizedError, NotFoundError, BadRequestError
from app.domain.portfolio.services.crypto_portfolio_service import (
    CryptoPortfolioService,
)
from app.domain.portfolio.services.crypto_service import CryptoService
from app.domain.portfolio.repositories.crypto_repository import CryptoRepository
from app.domain.portfolio.repositories.crypto_portfolio_repository import (
    CryptoPortfolioRepository,
)
from fastapi_pagination import Page, paginate
from app.domain.portfolio.schemas.crypto_portfolio_schemas import (
    CryptoPortfolioCreateSchema,
    CryptoPortfolioSchema,
    CryptoPortfolioUpdateSchema,
    CryptoPortfolioDetailSchema,
    CryptoPortfolioWatched,
    CryptoPortfolioTransactions,
    CryptoPortfolioTransactionDetail,
    CryptoPortfolioCreateTransaction,
    CryptoPortfolioUpdateTransaction,
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

    is_success = crypto_portfolio_service.delete_all_portfolios()

    return {
        "detail": (
            "Usunięto wszystkie portfele"
            if is_success
            else "Brak portfeli do usunięcia"
        )
    }


@router.get("/{portfolio_id}")
@limiter.limit("5/second")
def get_detail_portfolio_crypto(
    request: Request,
    portfolio_id: str,
    db: Session = Depends(get_db),
    user_id=Depends(authenticate),
) -> CryptoPortfolioDetailSchema:
    crypto_portfolio_repository = CryptoPortfolioRepository(db)
    crypto_portfolio_service = CryptoPortfolioService(
        crypto_portfolio_repository, user_id
    )
    try:
        crypto_portfolio = crypto_portfolio_service.get_portfolio_by_id(portfolio_id)
    except NotFoundError as ne:
        raise HTTPException(status_code=ne.status_code, detail=str(ne))
    except UnauthorizedError as ue:
        raise HTTPException(status_code=ue.status_code, detail=str(ue))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return crypto_portfolio


@router.patch("/{portfolio_id}")
@limiter.limit("1/second")
def update_portfolio_crypto(
    request: Request,
    portfolio_id: str,
    update_data: CryptoPortfolioUpdateSchema,
    user_id: Annotated[str, Depends(authenticate)],
    db: Session = Depends(get_db),
) -> CryptoPortfolioSchema:
    crypto_portfolio_repository = CryptoPortfolioRepository(db)
    crypto_portfolio_service = CryptoPortfolioService(
        crypto_portfolio_repository, user_id
    )
    try:
        crypto_portfolio = crypto_portfolio_service.update_portfolio(
            portfolio_id, update_data.model_dump()
        )
    except NotFoundError as ne:
        raise HTTPException(status_code=ne.status_code, detail=str(ne))
    except UnauthorizedError as ue:
        raise HTTPException(status_code=ue.status_code, detail=str(ue))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return crypto_portfolio


@router.delete("/{portfolio_id}")
@limiter.limit("1/second")
def delete_portfolio_crypto(
    request: Request,
    portfolio_id: str,
    db: Session = Depends(get_db),
    user_id=Depends(authenticate),
):
    crypto_portfolio_repository = CryptoPortfolioRepository(db)
    crypto_portfolio_service = CryptoPortfolioService(
        crypto_portfolio_repository, user_id
    )
    try:
        crypto_portfolio = crypto_portfolio_service.delete_portfolio(portfolio_id)
    except NotFoundError as ne:
        raise HTTPException(status_code=ne.status_code, detail=str(ne))
    except UnauthorizedError as ue:
        raise HTTPException(status_code=ue.status_code, detail=str(ue))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "detail": (
            "Usunięto portfel" if crypto_portfolio else "Brak portfela do usunięcia"
        )
    }


@router.post("/{portfolio_id}/watched_cryptos/{crypto_symbol}")
@limiter.limit("5/second")
def add_watched_crypto(
    request: Request,
    portfolio_id: str,
    crypto_symbol: str,
    user_id=Depends(authenticate),
    db: Session = Depends(get_db),
) -> CryptoPortfolioWatched:
    try:
        crypto_repository = CryptoRepository(db)
        crypto_service = CryptoService(crypto_repository)

        crypto_portfolio_repository = CryptoPortfolioRepository(db)
        crypto_portfolio_service = CryptoPortfolioService(
            crypto_portfolio_repository, user_id
        )

        crypto = crypto_service.get_crypto_by_symbol(crypto_symbol)
        crypto_portfolio = crypto_portfolio_service.get_portfolio_by_id(
            portfolio_id, validate_permission_to_edit=True
        )
        watched_crypto = crypto_portfolio_service.add_watched_crypto_to_portfolio(
            portfolio_id, crypto
        )
    except BadRequestError as bre:
        raise HTTPException(status_code=bre.status_code, detail=str(bre))
    except UnauthorizedError as ue:
        raise HTTPException(status_code=ue.status_code, detail=str(ue))
    except NotFoundError as ne:
        raise HTTPException(status_code=ne.status_code, detail=str(ne))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return watched_crypto


@router.delete("/{portfolio_id}/watched_cryptos/{crypto_symbol}")
@limiter.limit("5/second")
def remove_watched_crypto(
    request: Request,
    portfolio_id: str,
    crypto_symbol: str,
    user_id: str = Depends(authenticate),
    db: Session = Depends(get_db),
):
    try:
        crypto_repository = CryptoRepository(db)
        crypto_service = CryptoService(crypto_repository)

        crypto_portfolio_repository = CryptoPortfolioRepository(db)
        crypto_portfolio_service = CryptoPortfolioService(
            crypto_portfolio_repository, user_id
        )

        crypto = crypto_service.get_crypto_by_symbol(crypto_symbol)

        watched_crypto = crypto_portfolio_service.delete_watched_crypto_from_portfolio(
            portfolio_id, crypto
        )
    except BadRequestError as bre:
        raise HTTPException(status_code=bre.status_code, detail=str(bre))
    except UnauthorizedError as ue:
        raise HTTPException(status_code=ue.status_code, detail=str(ue))
    except NotFoundError as ne:
        raise HTTPException(status_code=ne.status_code, detail=str(ne))

    return {"detail": "Usunięto obserwowaną kryptowalutę z portfela"}


@router.delete("/{portfolio_id}/watched_cryptos")
@limiter.limit("1/second")
def remove_all_watched_cryptos(
    request: Request,
    portfolio_id: str,
    user_id: str = Depends(authenticate),
    db: Session = Depends(get_db),
):
    try:

        crypto_portfolio_repository = CryptoPortfolioRepository(db)
        crypto_portfolio_service = CryptoPortfolioService(
            crypto_portfolio_repository, user_id
        )

        watched_crypto = (
            crypto_portfolio_service.delete_all_watched_cryptos_from_portfolio(
                portfolio_id
            )
        )
    except BadRequestError as bre:
        raise HTTPException(status_code=bre.status_code, detail=str(bre))
    except UnauthorizedError as ue:
        raise HTTPException(status_code=ue.status_code, detail=str(ue))
    except NotFoundError as ne:
        raise HTTPException(status_code=ne.status_code, detail=str(ne))

    return {"detail": "Usunięto wszystkie obserwowane kryptowaluty z portfela"}


@router.get("/{portfolio_id}/transactions")
@limiter.limit("5/second")
def get_portfolio_crypto_transactions(
    request: Request,
    portfolio_id: str,
    user_id: str = Depends(authenticate),
    db: Session = Depends(get_db),
) -> Page[CryptoPortfolioTransactions]:
    try:

        crypto_portfolio_repository = CryptoPortfolioRepository(db)
        crypto_portfolio_service = CryptoPortfolioService(
            crypto_portfolio_repository, user_id
        )

        transactions = crypto_portfolio_service.get_transactions_in_portfolio(
            portfolio_id
        )
    except BadRequestError as bre:
        raise HTTPException(status_code=bre.status_code, detail=str(bre))
    except UnauthorizedError as ue:
        raise HTTPException(status_code=ue.status_code, detail=str(ue))
    except NotFoundError as ne:
        raise HTTPException(status_code=ne.status_code, detail=str(ne))

    return paginate(transactions)


@router.post("/{portfolio_id}/transactions")
@limiter.limit("5/second")
def create_portfolio_crypto_transaction(
    request: Request,
    portfolio_id: str,
    transaction_data: CryptoPortfolioCreateTransaction,
    user_id: str = Depends(authenticate),
    db: Session = Depends(get_db),
) -> CryptoPortfolioTransactionDetail:

    try:
        crypto_repository = CryptoRepository(db)
        crypto_service = CryptoService(crypto_repository)

        crypto_portfolio_repository = CryptoPortfolioRepository(db)
        crypto_portfolio_service = CryptoPortfolioService(
            crypto_portfolio_repository, user_id
        )

        transaction_data = transaction_data.model_dump()
        crypto = crypto_service.get_crypto_by_symbol(
            transaction_data["crypto"]["symbol"]
        )
        transaction_data.update({"portfolio_id": portfolio_id, "crypto": crypto})
        created_transaction = crypto_portfolio_service.create_transaction_in_portfolio(
            portfolio_id, transaction_data
        )
    except BadRequestError as bre:
        raise HTTPException(status_code=bre.status_code, detail=str(bre))
    except UnauthorizedError as ue:
        raise HTTPException(status_code=ue.status_code, detail=str(ue))
    except NotFoundError as ne:
        raise HTTPException(status_code=ne.status_code, detail=str(ne))

    return created_transaction


@router.get("/{portfolio_id}/transactions/{transaction_id}")
@limiter.limit("5/second")
def get_detail_portfolio_crypto_transaction(
    request: Request,
    portfolio_id: str,
    transaction_id: str,
    user_id: str = Depends(authenticate),
    db: Session = Depends(get_db),
) -> CryptoPortfolioTransactionDetail:
    try:

        crypto_portfolio_repository = CryptoPortfolioRepository(db)
        crypto_portfolio_service = CryptoPortfolioService(
            crypto_portfolio_repository, user_id
        )

        transaction = crypto_portfolio_service.get_transaction_in_portfolio(
            portfolio_id, transaction_id
        )
    except BadRequestError as bre:
        raise HTTPException(status_code=bre.status_code, detail=str(bre))
    except UnauthorizedError as ue:
        raise HTTPException(status_code=ue.status_code, detail=str(ue))
    except NotFoundError as ne:
        raise HTTPException(status_code=ne.status_code, detail=str(ne))

    return transaction


@router.patch("/{portfolio_id}/transactions/{transaction_id}")
@limiter.limit("5/second")
def update_portfolio_crypto_transaction(
    request: Request,
    portfolio_id: str,
    transaction_id: str,
    update_transaction_data: CryptoPortfolioUpdateTransaction,
    user_id: str = Depends(authenticate),
    db: Session = Depends(get_db),
) -> CryptoPortfolioTransactionDetail:

    try:
        crypto_repository = CryptoRepository(db)
        crypto_service = CryptoService(crypto_repository)

        crypto_portfolio_repository = CryptoPortfolioRepository(db)
        crypto_portfolio_service = CryptoPortfolioService(
            crypto_portfolio_repository, user_id
        )

        update_transaction_data = update_transaction_data.model_dump()
        crypto = update_transaction_data.get("crypto", None)
        if crypto is None:
            pass
        else:
            crypto = crypto_service.get_crypto_by_symbol(
                update_transaction_data["crypto"].get("symbol", None)
            )

        update_transaction_data.update({"crypto": crypto, "portfolio_id": portfolio_id})
        created_transaction = crypto_portfolio_service.update_transaction_in_portfolio(
            portfolio_id, transaction_id, update_transaction_data
        )
    except BadRequestError as bre:
        raise HTTPException(status_code=bre.status_code, detail=str(bre))
    except UnauthorizedError as ue:
        raise HTTPException(status_code=ue.status_code, detail=str(ue))
    except NotFoundError as ne:
        raise HTTPException(status_code=ne.status_code, detail=str(ne))

    return created_transaction


@router.delete("/{portfolio_id}/transactions/{transaction_id}")
@limiter.limit("5/second")
def delete_portfolio_crypto_transaction(
    request: Request,
    portfolio_id: str,
    transaction_id: str,
    user_id: str = Depends(authenticate),
    db: Session = Depends(get_db),
):
    try:

        crypto_portfolio_repository = CryptoPortfolioRepository(db)
        crypto_portfolio_service = CryptoPortfolioService(
            crypto_portfolio_repository, user_id
        )

        transaction = crypto_portfolio_service.delete_transaction_in_portfolio(
            portfolio_id, transaction_id
        )
    except BadRequestError as bre:
        raise HTTPException(status_code=bre.status_code, detail=str(bre))
    except UnauthorizedError as ue:
        raise HTTPException(status_code=ue.status_code, detail=str(ue))
    except NotFoundError as ne:
        raise HTTPException(status_code=ne.status_code, detail=str(ne))

    return {"detail": "Usunięto transakcję z portfela"}


@router.delete("/{portfolio_id}/transactions")
@limiter.limit("5/second")
def delete_portfolio_crypto_transactions(
    request: Request,
    portfolio_id: str,
    user_id: str = Depends(authenticate),
    db: Session = Depends(get_db),
):
    try:

        crypto_portfolio_repository = CryptoPortfolioRepository(db)
        crypto_portfolio_service = CryptoPortfolioService(
            crypto_portfolio_repository, user_id
        )

        transaction = crypto_portfolio_service.delete_all_transactions_in_portfolio(
            portfolio_id
        )
    except BadRequestError as bre:
        raise HTTPException(status_code=bre.status_code, detail=str(bre))
    except UnauthorizedError as ue:
        raise HTTPException(status_code=ue.status_code, detail=str(ue))
    except NotFoundError as ne:
        raise HTTPException(status_code=ne.status_code, detail=str(ne))

    return {"detail": "Usunięto wszystkie transakcje z portfela"}
